import dataclasses
import itertools
import logging
import time
from collections import defaultdict
from typing import Callable, Any, List, Tuple, Dict, Set
from uuid import UUID

from asgiref.sync import sync_to_async
from langchain.schema.runnable import (
    RunnableSerializable,
    RunnableSequence,
    RunnableParallel,
    Runnable,
)
from langchain.schema.runnable.utils import Input, Output

from ix.api.components.types import NodeType as NodeTypePydantic
from ix.api.chains.types import Node as NodePydantic, InputConfig
from ix.chains.components.lcel import init_sequence, init_branch
from ix.chains.fixture_src.flow import ROOT_CLASS_PATH
from ix.chains.loaders.context import IxContext

from ix.chains.loaders.prompts import load_prompt
from ix.chains.loaders.templates import NodeTemplate
from ix.chains.models import NodeType, ChainNode, ChainEdge, Chain
from ix.runnable.flow import MergeList
from ix.runnable.ix import IxNode
from ix.secrets.models import Secret
from ix.utils.config import format_config
from ix.utils.importlib import import_class

import_node_class = import_class


logger = logging.getLogger(__name__)


RUNNABLE_TYPES = {
    "agent",
    "chain",
    "llm",
    "prompt",
    "retriever",
    "tool",
}


def get_node_loader(name: str) -> Callable:
    """
    Get a node config loader by node type.

    Used to manipulate a nodes config before loading it
    """
    from ix.chains.loaders.memory import load_memory_config
    from ix.chains.loaders.memory import load_chat_memory_backend_config

    return {
        "memory": load_memory_config,
        "memory_backend": load_chat_memory_backend_config,
        "prompt": load_prompt,
    }.get(name, None)


def get_property_loader(name: str) -> Callable:
    """Get a property loader.

    Used to customize loading a property by key.
    """
    from ix.chains.loaders.memory import load_memory_property
    from ix.chains.loaders.retriever import load_retriever_property
    from ix.chains.loaders.tools import load_tool_property

    return {
        "memory": load_memory_property,
        "retriever": load_retriever_property,
        "tool": load_tool_property,
    }.get(name, None)


def get_node_initializer(node_type: str) -> Callable:
    """Get a node initializer

    Fetches a custom initializer to be used instead of the class initializer.
    Used to add shims around specific types of nodes.
    """
    from ix.chains.loaders.text_splitter import initialize_text_splitter
    from ix.chains.loaders.vectorstore import initialize_vectorstore

    return {
        "text_splitter": initialize_text_splitter,
        "vectorstore": initialize_vectorstore,
    }.get(node_type, None)


def load_secrets(config: dict, node_type: NodeType):
    """Load secrets from vault into the config dict"""

    if not node_type.fields:
        return

    # build map of secrets to load
    to_load = set()
    for field in node_type.fields:
        if field["input_type"] == "secret":
            if field["name"] not in config:
                continue
            secret_id = config[field["name"]]
            if secret_id:
                to_load.add(secret_id)

    # load secrets and update config
    # TODO: need user here to limit access to secrets
    secrets = Secret.objects.filter(id__in=set(to_load))
    for secret in secrets:
        try:
            value = secret.read()
        except Exception as e:
            logger.error(f"Failed to load secret {secret.id}: {e}")
            raise Exception(f"Failed to load secret: {secret.id}")
        to_load.remove(str(secret.id))
        config.update(value)

    if to_load:
        raise ValueError(f"Secrets not found: {to_load}")


def load_node(
    node: ChainNode,
    context: IxContext,
    variables: Dict[str, Any] = None,
    as_template: bool = False,
) -> Any:
    """
    Generic loader for loading the Langchain component a ChainNode represents.

    This loader will load the component and its config, and then recursively
    load any properties that are attached to the node. The loader also handles
    recursively loading any child nodes that are attached to the node.
    """

    logger.debug(f"Loading chain for name={node.name} class_path={node.class_path}")
    start_time = time.time()
    node_type: NodeType = node.node_type
    node_type_pydantic = NodeTypePydantic.model_validate(node_type)
    config = node.config.copy() if node.config else {}

    # TODO: implement resolve secrets from vault and settings from vocabulary
    #       neither of these subsystems are implemented yet. For now load all
    #       values as text from config dict
    # resolve secrets and settings
    # format the config in this order:
    # 1. format with context variables
    # 2. format with secrets
    if variables is not None:
        config = format_config(config, variables)
    elif as_template:
        return NodeTemplate(node, context)
    load_secrets(config, node_type)

    # load type specific config options. This is generally for loading
    # ix specific features into the config dict
    if node_loader := get_node_loader(node_type.type):
        logger.debug(
            f"Loading config with node config loader for type={node_type.type}"
        )
        config = node_loader(node, context)

    # prepare properties for loading. Properties should be grouped by key.
    properties = node.incoming_edges.filter(relation="PROP").order_by("target_key")
    for group in itertools.groupby(properties, lambda x: x.target_key):
        key, edges = group
        edge_group: List[ChainEdge] = [edge for edge in edges]
        logger.debug(f"Loading property target_key={key} edge_group={edge_group}")

        # choose the type the incoming connection is processed as. If the source node
        # will be converted to another type, use the as_type defined on the connection
        # this allows a single property loader to encapsulate any necessary conversions.
        # e.g. retriever converting Vectorstore.
        connector = node_type.connectors_as_dict[key]
        as_type = connector.get("as_type", None) or edge_group[0].source.node_type.type
        connector_is_template = connector.get("template", False)

        if connector.get("collection", None):
            # load connector as a collection

            config[key] = load_collection(
                connector,
                edge_group,
                context,
                variables=variables,
                # TODO: will templates be allowed in collections?
                # as_template=connector_is_template,
            )
        elif property_loader := get_property_loader(as_type):
            # load type specific config options. This is generally for loading
            # ix specific features into the config dict
            logger.debug(f"Loading with property loader for type={node_type.type}")
            config[key] = property_loader(edge_group, context)
        else:
            # default recursive property loading
            if connector.get("multiple", False):
                config[key] = [
                    load_node(
                        edge.source,
                        context,
                        variables=variables,
                        as_template=connector_is_template,
                    )
                    for edge in edge_group
                ]
            else:
                if len(edge_group) > 1:
                    raise ValueError(f"Multiple values for {key} not allowed")
                config[key] = load_node(
                    edge_group[0].source,
                    context,
                    variables=variables,
                    as_template=connector_is_template,
                )

    # converted flattened property groups back into nested properties. Fields with
    # the same parent are grouped together into a single object. By default, groups
    # are dicts but this can be overridden by setting the field_group's class_path
    property_groups = defaultdict(list)
    for field in node_type.fields or []:
        if field.get("parent"):
            property_groups[field["parent"]].append(field)
    for key, property_group_fields in property_groups.items():
        logger.debug(f"key={key} property_group_fields={property_group_fields}")
        config[key] = {
            field["name"]: config.pop(field["name"])
            for field in property_group_fields
            if field["name"] in config
        }
    if node_type.field_groups:
        for key, field_group in node_type.field_groups.items():
            if field_group_class_path := field_group.get("class_path"):
                config[key] = import_node_class(field_group_class_path)(**config[key])

    # load component class and initialize. A type specific initializer may be used here
    # for initialization common to all components of that type.
    node_class = import_node_class(node.class_path)
    node_initializer = get_node_initializer(node_type.type)

    # use name and description from ChainNode.
    if "name" not in config and "name" in node_type_pydantic.field_map:
        config["name"] = node.name
    if "description" not in config and "description" in node_type_pydantic.field_map:
        config["description"] = node.description

    # filter out config values that are not passed to the initializer
    if node_type_pydantic.init_exclude:
        config = {
            key: value
            for key, value in config.items()
            if key not in node_type_pydantic.init_exclude
        }

    try:
        if node_initializer:
            instance = node_initializer(node.class_path, config)
        else:
            instance = node_class(**config)
    except Exception:
        logger.error(f"Exception loading node class={node.class_path}")
        raise
    logger.debug(f"Loaded node class={node.class_path} in {time.time() - start_time}s")

    return instance


def load_collection(
    connector: dict,
    edge_group: List[ChainEdge],
    context: IxContext,
    variables: Dict[str, Any] = None,
) -> RunnableSerializable | List[Tuple[str, RunnableSerializable]]:
    """Load connector as a collection (list, map, map-tuples, etc). These properties
    are special in that the graph is traversed and contained within flow control
    `Runnable` such as `RunnableSequence`, `RunnableMa`p, etc. This bridges the gap
    between how a graph is structured as nodes  &edges in the database/UX and how it
    is represented with LangChain Expression Language components.
    """
    connector_is_template = connector.get("template", False)
    collection_type = connector.get("collection", None)

    if collection_type in {"flow"}:
        if collection_type == "flow":
            # load property as a Runnable flow
            nodes = [edge.source for edge in edge_group]
            return init_flow_node(nodes, context=context, variables=variables)
    elif collection_type == "map":
        return {
            edge.map_key: load_node(
                edge.source,
                context,
                variables=variables,
                as_template=connector_is_template,
            )
            for edge in edge_group
        }
    elif collection_type == "map_tuples":
        return [
            (
                edge.map_key,
                load_node(
                    edge.source,
                    context,
                    variables=variables,
                    as_template=connector_is_template,
                ),
            )
            for edge in edge_group
        ]
    else:
        raise ValueError(f"Unknown collection type: {collection_type}")


@dataclasses.dataclass
class AggPlaceholder:
    type: str
    steps: List["FlowPlaceholder"]

    def id(self):
        return id(self)

    def __eq__(self, other):
        # step order doesn't matter
        if isinstance(other, AggPlaceholder):
            return self.type == other.type and set(self.steps) == set(other.steps)
        return False

    @classmethod
    def for_connector(
        cls, connector: dict, steps: List["FlowPlaceholder"]
    ) -> "AggPlaceholder":
        collection = connector.get("collection", "list") if connector else "list"
        return cls(type=collection, steps=steps)


@dataclasses.dataclass
class MapPlaceholder:
    node: ChainNode
    map: Dict[str, "FlowPlaceholder"]
    branch_depths: Set[Tuple[str]] = dataclasses.field(
        default_factory=lambda: {tuple()}
    )

    @property
    def id(self):
        return self.node.id

    @property
    def spans_branches(self) -> bool:
        return len(self.branch_depths) > 1

    def __eq__(self, other):
        # exclude branch depths from equality check
        if isinstance(other, MapPlaceholder):
            return self.node.id == other.node.id and self.map == other.map
        return False


@dataclasses.dataclass
class ImplicitJoin:
    """Represents a joining point of multiple paths that meet at a single node that isn't
    a Map.

    The join is either an implicit map or an implicit post-branch join. It can't be
    known which until all incoming branches are explored.

    This class acts as a placeholder in the first pass. It is converted to either a Map
    or a sequence of nodes in the second pass.
    """

    source: ChainNode | List[ChainNode]
    target: MapPlaceholder
    """map of nodes grouped by target keys"""

    @property
    def id(self):
        return self.target.id

    def resolve(self) -> MapPlaceholder | List[ChainNode]:
        """Resolve into either a Map or a sequence of nodes based on whether the incoming
        links to the join target are within the same branch or across multiple branches.
        """
        if self.target.spans_branches:
            # return as sequence
            if isinstance(self.source, list):
                return self.source + [self.target.node]
            return [self.source, self.target.node]
        else:
            # return as map
            return self.target


@dataclasses.dataclass
class BranchPlaceholder:
    node: ChainNode
    branches: List[Tuple[str, "FlowPlaceholder"]]
    default: "FlowPlaceholder"

    @property
    def id(self):
        return self.node.id


FlowPlaceholder = (
    ChainNode
    | SequencePlaceholder
    | MapPlaceholder
    | BranchPlaceholder
    | ImplicitJoin
    | AggPlaceholder
    | List["FlowPlaceholder"]
)


def init_chain_flow(
    chain: Chain, context: IxContext, variables: Dict[str, Any] = None
) -> Runnable:
    """
    Initialize a flow from a chain.
    """
    flow_root = load_chain_flow(chain=chain)
    logger.debug(f"init_chain_flow chain={chain.id} flow_root={flow_root}")
    return init_flow_node(flow_root, context=context, variables=variables)


async def ainit_chain_flow(
    chain: Chain, context: IxContext, variables: Dict[str, Any] = None
):
    return await sync_to_async(init_chain_flow)(chain, context, variables)


def init_flow(
    nodes: List[ChainNode],
    context: IxContext,
    variables: Dict[str, Any] = None,
    seen: Dict[UUID, "FlowPlaceholder"] = None,
) -> Runnable[Input, Output] | List[Runnable[Input, Output]]:
    flow_roots = load_flow_node(nodes, seen=seen)
    if not isinstance(flow_roots, list):
        flow_roots = [flow_roots]

    flows = []
    for flow_root in flow_roots:
        flows.append(init_flow_node(flow_root, context=context, variables=variables))

    if len(flows) == 1:
        return flows[0]
    return flows


async def ainit_flow(
    nodes: List[ChainNode],
    context: IxContext,
    variables: Dict[str, Any] = None,
    seen: Dict[UUID, "FlowPlaceholder"] = None,
) -> Runnable:
    return await sync_to_async(init_flow)(nodes, context, variables, seen)


def load_chain_flow(chain: Chain) -> FlowPlaceholder:
    try:
        root = chain.nodes.get(root=True, class_path=ROOT_CLASS_PATH)
        nodes = chain.nodes.filter(incoming_edges__source=root)
        logger.debug(f"Loading chain flow with roots: {root}")
    except ChainNode.DoesNotExist:
        # fallback to old style roots:
        # TODO: remove this fallback after all chains have been migrated
        nodes = chain.nodes.filter(root=True)
        logger.debug(f"Loading chain flow with roots: {nodes}")

    return load_flow_node(nodes)


async def aload_chain_flow(chain: Chain) -> FlowPlaceholder:
    return await sync_to_async(load_chain_flow)(chain)


def load_flow_node(
    nodes: List[ChainNode], seen: Dict[UUID, "FlowPlaceholder"] = None
) -> FlowPlaceholder | List[FlowPlaceholder]:
    """Loads a node or group of node connected to a map"""
    if len(nodes) == 0:
        raise ValueError("No root nodes found")

    branch_depth = tuple()
    seen = seen or {}
    if len(nodes) == 1:
        return load_flow_sequence(nodes[0], seen, branch_depth=branch_depth)
    return load_flow_map(nodes, seen, branch_depth=branch_depth)


async def aload_flow_node(
    nodes: List[ChainNode], seen: Dict[UUID, "FlowPlaceholder"] = None
) -> FlowPlaceholder | List[FlowPlaceholder]:
    return await sync_to_async(load_flow_node)(nodes, seen)


def load_flow_map(
    nodes: List[ChainNode],
    seen: Dict[UUID, FlowPlaceholder],
    branch_depth: Tuple[str] = None,
) -> FlowPlaceholder | List[FlowPlaceholder]:
    """
    Load all paths starting from the given group of nodes. The returned nodes are
    the set of distinct flows that should be created given the input nodes:

    - distinct/disjoint paths are returned.
    - map nodes are de-duped and returned as a single map node.

    Example single flow:
    Each.workflow --> Foo --> Bar --> Baz

    Example multiple flows:
    Agent.tools --> Foo --> Bar --> Baz
                --> SearchTool
    """
    local_seen: Dict[UUID, FlowPlaceholder] = {}
    new_nodes: List[FlowPlaceholder] = []
    for node in nodes:
        # Load & dedupe returned nodes:
        # The first branch is explored the deepest. Subsequent runs fill in missing
        # branches from the first run. The first run will always be complete after
        # all branches have been processed.
        loaded_node = load_flow_sequence(node, seen=seen, branch_depth=branch_depth)
        node_id = loaded_node[0].id if isinstance(loaded_node, list) else loaded_node.id
        if node_id in local_seen:
            local_seen.update(seen)
            continue
        local_seen.update(seen)
        new_nodes.append(loaded_node)

    if len(new_nodes) == 1:
        return new_nodes[0]

    return new_nodes


def load_flow_branch(
    node: ChainNode,
    seen: Dict[UUID, FlowPlaceholder],
    branch_depth: Tuple[str] = None,
) -> BranchPlaceholder:
    # gather branches
    outgoing_links = (
        node.outgoing_edges.select_related("target")
        .filter(relation="LINK")
        .order_by("source_key")
    )
    branches = {}
    for key, group in itertools.groupby(outgoing_links, lambda edge: edge.source_key):
        _branch_depth = branch_depth + (key,) if branch_depth else (key,)
        group_as_list = list(group)
        if len(group_as_list) > 1:
            targets = [edge.target for edge in group_as_list]
            nodes = load_flow_map(targets, seen=seen, branch_depth=_branch_depth)
        else:
            nodes = load_flow_sequence(
                group_as_list[0].target, seen=seen, branch_depth=_branch_depth
            )
        branches[key] = nodes

    # build sorted list from branch node's config
    branch_keys = node.config.get("branches", [])
    branch_uuids = node.config.get("branches_hash", [])
    branch_tuples = [
        (key, branches[branch_uuid])
        for key, branch_uuid in zip(branch_keys, branch_uuids)
    ]

    if "default" not in branches:
        raise ValueError("Branch node must have a default branch")

    return BranchPlaceholder(
        node=node,
        default=branches["default"],
        branches=branch_tuples
    )


BRANCH_CLASS_PATH = "ix.chains.components.lcel.init_branch"
MAP_CLASS_PATH = "ix.chains.components.lcel.init_parallel"


def load_flow_sequence(
    start: ChainNode,
    seen: Dict[UUID, FlowPlaceholder],
    branch_depth: Tuple[str] = None,
) -> Runnable | SequencePlaceholder:
    sequential_nodes = []

    # traverse the sequence
    current = start
    infinite_loop_safety_count = 0
    while infinite_loop_safety_count < 1000:
        infinite_loop_safety_count += 1

        outgoing_links = list(
            current.outgoing_edges.select_related("target").filter(relation="LINK")
        )
        incoming_links = list(current.incoming_edges.filter(relation="LINK"))

        # single outgoing link
        # TODO: non map nodes with multiple incoming links require a map node.
        if current.class_path == MAP_CLASS_PATH or len(incoming_links) > 1:
            # Since MAP node comes after the branches feeding into it,
            # look at incoming LINKs
            was_seen = current.id in seen
            node_map = seen.setdefault(current.id, MapPlaceholder(node=current, map={}))

            # unpack if single item
            map_sequence = sequential_nodes
            if isinstance(sequential_nodes, list) and len(sequential_nodes) == 1:
                map_sequence = sequential_nodes[0]

            if False and current.root:
                # TODO: add passthrough from root input
                # auto add passthrough lambda for root input
                # map_sequence = [RunnableLambda(lambda x: x[target_key])]
                pass

            elif len(sequential_nodes) == 0:
                # TODO: add auto passthrough.
                # no incoming links for now do nothing.
                pass
                # if incoming link targets "in" then all keys are taken as input
                # if incoming link does not target "in" then just that input is taken
                # if incoming link source is "out" then and target is not "in" then input[target_key]

            else:
                # has incoming links
                # resolve the map edge hash into the key
                try:
                    incoming_link = current.incoming_edges.get(
                        relation="LINK", source_id=sequential_nodes[-1].id
                    )
                except ChainEdge.DoesNotExist:
                    raise Exception(
                        f"Unable to find incoming link from {sequential_nodes[-1]} "
                        f"to map node {current}"
                    )
                if current.class_path == MAP_CLASS_PATH:
                    target_key = incoming_link.target_key
                    step_index = current.config["steps_hash"].index(target_key)
                    map_key = current.config["steps"][step_index]
                    next_node = node_map
                else:
                    # implicit map & aggregator
                    map_key = incoming_link.target_key
                    connector = current.node_type.connectors_as_dict.get(map_key, None)

                    # current sequence + join target stored.
                    next_node = ImplicitJoin(source=sequential_nodes, target=node_map)

                    # aggregate with existing map where multiple links are joining.
                    if map_key in node_map.map:
                        aggregate = connector is None or connector.get("multiple", True)
                        aggregator = node_map.map[map_key]
                        if aggregate:
                            # new aggregator
                            if not isinstance(aggregator, AggPlaceholder):
                                aggregator = AggPlaceholder.for_connector(
                                    connector=connector,
                                    steps=map_sequence,
                                )
                                node_map.map[map_key] = aggregator
                            # append to existing aggregator
                            else:
                                if len(map_sequence.steps) == 1:
                                    map_sequence.steps.append(sequential_nodes[0])
                                else:
                                    map_sequence.steps.append(sequential_nodes)
                        else:
                            raise ValueError(
                                "Received multiple values for a single key"
                            )

                    else:
                        aggregate = connector and connector.get("multiple", False)
                        if aggregate:
                            # TODO: this is repacking after unpacking above.
                            if not isinstance(map_sequence, list):
                                map_sequence = [map_sequence]
                            map_sequence = AggPlaceholder.for_connector(
                                connector=connector,
                                steps=map_sequence,
                            )

                node_map.map[map_key] = map_sequence
                node_map.branch_depths.add(branch_depth)

            # the prior sequence rolled up into the map
            sequential_nodes = [next_node]

            # only first iteration traverses past a map. Implicit join
            # still requires full traversal on all branches.
            if was_seen and not isinstance(next_node, ImplicitJoin):
                break

        elif current.class_path == BRANCH_CLASS_PATH:
            # start of explicitly defined branch
            branch_placeholder = load_flow_branch(
                current, seen=seen, branch_depth=branch_depth
            )
            sequential_nodes.append(branch_placeholder)

            # branches must be fully explored so there is nothing remaining to traverse
            break
        else:
            # Add nodes that were not already added in the forward traversal for
            # a map node. This includes map node and last node in the map sequence
            if current.class_path != MAP_CLASS_PATH and (
                not sequential_nodes or sequential_nodes[-1] != current
            ):
                if current.id in seen:
                    sequential_nodes.append(seen[current.id])
                else:
                    sequential_nodes.append(current)
                    seen[current.id] = current

        if len(outgoing_links) > 1 and current.class_path != BRANCH_CLASS_PATH:
            # multiple links: start of split that will end in a map node.
            targets = [link.target for link in outgoing_links]
            map_node = load_flow_map(targets, seen=seen, branch_depth=branch_depth)

            # add to sequence
            if isinstance(map_node, list):
                sequential_nodes.extend(map_node)
            elif isinstance(map_node, MapPlaceholder):
                sequential_nodes.append(map_node)
            else:
                raise ValueError(
                    f"unsupported return type after processing flow split. type={type(map_node)}"
                )

            # all branches explored past the map node
            break

        elif len(outgoing_links) == 0:
            break
        else:
            current = outgoing_links[0].target

    if len(sequential_nodes) == 1:
        return sequential_nodes[0]
    else:
        return sequential_nodes


def init_flow_node(
    root: FlowPlaceholder,
    context: IxContext,
    variables: Dict[str, Any] = None,
    **kwargs,
) -> Runnable:
    """Initial a flow node

    Assumes a collection of ChainNodes and placeholders constructed by load_flow.
    """
    if isinstance(root, ChainNode):
        node_type = NodeTypePydantic.model_validate(root.node_type)
        instance = load_node(root, context=context, variables=variables)

        if isinstance(instance, Runnable):
            instance = IxNode(
                node_id=root.id,
                child=instance,
                context=context,
                config=root.config,
                bind_points=node_type.bind_points,
            )
        return instance
    elif isinstance(root, BranchPlaceholder):
        return init_branch(
            default=init_flow_node(root.default, context=context, variables=variables),
            branches=[
                (key, init_flow_node(branch, context=context, variables=variables))
                for key, branch in root.branches
            ],
        )
    elif isinstance(root, MapPlaceholder):
        runnable_map = RunnableParallel(
            **{
                key: init_flow_node(node, context=context, variables=variables)
                for key, node in root.map.items()
            }
        )
        if root.node.class_path == MAP_CLASS_PATH:
            return runnable_map
        else:
            # create an implicit [map -> node] sequence.
            sequence = runnable_map | init_flow_node(
                root.node, context=context, variables=variables
            )
            return sequence
    elif isinstance(root, list):
        nodes = [
            init_flow_node(node, context=context, variables=variables) for node in root
        ]
        return init_sequence(steps=nodes)
    elif isinstance(root, AggPlaceholder):
        return MergeList(
            steps=[
                init_flow_node(node, context=context, variables=variables)
                for node in root.steps
            ]
        )
    elif isinstance(root, ImplicitJoin):
        return init_flow_node(root.resolve(), context=context, variables=variables)

    else:
        raise Exception("Invalid flow type: " + str(type(root)))
