import itertools
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Any, List, Tuple, Dict

from asgiref.sync import sync_to_async
from langchain.schema.runnable import (
    RunnableSerializable,
    RunnableSequence,
    RunnableParallel,
    Runnable,
)

from ix.chains.components.lcel import init_sequence, init_branch
from ix.chains.fixture_src.flow import ROOT_CLASS_PATH
from ix.chains.loaders.context import IxContext

from ix.chains.loaders.prompts import load_prompt
from ix.chains.loaders.templates import NodeTemplate
from ix.chains.models import NodeType, ChainNode, ChainEdge, Chain
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

    return {
        "memory": load_memory_property,
        "retriever": load_retriever_property,
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
            node_group = [edge.source for edge in edge_group]
            config[key] = property_loader(node_group, context)
        else:
            # default recursive property loading
            if connector.get("multiple", False):
                config[key] = [
                    init_flow_node(edge.source, context) for edge in edge_group
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


@dataclass
class MapPlaceholder:
    node: ChainNode
    map: Dict[str, "FlowPlaceholder"]


@dataclass
class BranchPlaceholder:
    node: ChainNode
    branches: List[Tuple[str, "FlowPlaceholder"]]
    default: "FlowPlaceholder"


FlowPlaceholder = (
    ChainNode | List["FlowPlaceholder"] | MapPlaceholder | BranchPlaceholder
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
    nodes: List[ChainNode], context: IxContext, variables: Dict[str, Any] = None
) -> Runnable:
    flow_root = load_flow_node(nodes)
    return init_flow_node(flow_root, context=context, variables=variables)


async def ainit_flow(
    nodes: List[ChainNode], context: IxContext, variables: Dict[str, Any] = None
) -> Runnable:
    return await sync_to_async(init_flow)(nodes, context, variables)


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


def load_flow_node(nodes: List[ChainNode]) -> FlowPlaceholder:
    """Loads a node or group of node connected to a map"""
    if len(nodes) == 0:
        raise ValueError("No root nodes found")

    seen = {}
    if len(nodes) == 1:
        return load_flow_sequence(nodes[0], seen)
    return load_flow_map(nodes, seen)


async def aload_flow_node(chain: Chain, context=None, variables=None) -> None:
    return await sync_to_async(load_flow_node)(chain)


def load_flow_map(
    nodes: List[ChainNode],
    seen: Dict[str, FlowPlaceholder],
) -> FlowPlaceholder:
    logger.debug(">>>LOADING MAP")
    new_nodes = []
    for node in nodes:
        logger.debug(f">>>>>>> {node}")
        new_nodes = load_flow_sequence(node, seen=seen)

    # Nested maps collapse into the last node where all branches of the edges
    # merge back in. It doesn't matter which return value is used here since
    # they are all the same.
    return new_nodes


def load_flow_branch(
    node: ChainNode,
    seen: Dict[str, FlowPlaceholder],
) -> BranchPlaceholder:
    # gather branches
    outgoing_links = (
        node.outgoing_edges.select_related("target")
        .filter(relation="LINK")
        .order_by("source_key")
    )
    branches = {}
    for key, group in itertools.groupby(outgoing_links, lambda edge: edge.source_key):
        group_as_list = list(group)
        if len(group_as_list) > 1:
            targets = [edge.target for edge in group_as_list]
            nodes = load_flow_map(targets, seen=seen)
        else:
            nodes = load_flow_sequence(group_as_list[0].target, seen=seen)
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
        node=node, default=branches["default"], branches=branch_tuples
    )


BRANCH_CLASS_PATH = "ix.chains.components.lcel.init_branch"
MAP_CLASS_PATH = "ix.chains.components.lcel.init_parallel"


def load_flow_sequence(
    start: ChainNode,
    seen: Dict[str, FlowPlaceholder],
) -> Runnable | RunnableSequence:
    sequential_nodes = []

    # traverse the sequence
    current = start
    infinite_loop_safety_count = 0
    while infinite_loop_safety_count < 1000:
        infinite_loop_safety_count += 1

        outgoing_links = list(
            current.outgoing_edges.select_related("target").filter(relation="LINK")
        )

        if len(outgoing_links) > 1 and current.class_path != BRANCH_CLASS_PATH:
            # multiple links: start of implicitly defined map
            targets = [link.target for link in outgoing_links]
            map_nodes = load_flow_map(targets, seen=seen)
            sequential_nodes.append(current)
            sequential_nodes.extend(
                map_nodes if isinstance(map_nodes, list) else [map_nodes]
            )

            # Node for next iteration is the last node in the sequence that is returned
            current = sequential_nodes[-1]
            if isinstance(current, MapPlaceholder):
                current = current.node

        else:
            # single outgoing link
            if outgoing_links and outgoing_links[0].target.class_path == MAP_CLASS_PATH:
                # Since MAP node comes after the branches feeding into it,
                # look at outgoing LINKs to determine if the current sequence
                # should be aggregated forward into it.
                target = outgoing_links[0].target
                node_map = seen.setdefault(
                    target.id, MapPlaceholder(node=target, map={})
                )
                if not sequential_nodes:
                    map_sequence = current
                elif current.class_path == MAP_CLASS_PATH:
                    map_sequence = sequential_nodes
                else:
                    map_sequence = sequential_nodes + [current]
                if isinstance(map_sequence, list) and len(map_sequence) == 1:
                    map_sequence = map_sequence[0]

                # resolve the map connector hash into the key
                target_key = outgoing_links[0].target_key
                step_index = target.config["steps_hash"].index(target_key)
                map_key = target.config["steps"][step_index]
                node_map.map[map_key] = map_sequence

                # add to sequence here since it's a placeholder and current
                # must be a node
                sequential_nodes = [node_map]

                current = target
                continue

            elif current.class_path == BRANCH_CLASS_PATH:
                # start of explicitly defined branch
                branch_placeholder = load_flow_branch(current, seen=seen)
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

            if len(outgoing_links) == 0:
                break

            # there should only be one outgoing link here.
            current = outgoing_links[0].target

    if len(sequential_nodes) == 1:
        return sequential_nodes[0]
    else:
        return sequential_nodes


def init_flow_node(
    root: FlowPlaceholder, context: IxContext, variables: Dict[str, Any] = None
) -> Runnable:
    """Initial a flow node

    Assumes a collection of ChainNodes and placeholders constructed by load_flow.
    """

    if isinstance(root, ChainNode):
        return load_node(root, context=context, variables=variables)
    elif isinstance(root, BranchPlaceholder):
        return init_branch(
            default=init_flow_node(root.default, context=context, variables=variables),
            branches=[
                (key, init_flow_node(branch, context=context, variables=variables))
                for key, branch in root.branches
            ],
        )
    elif isinstance(root, MapPlaceholder):
        return RunnableParallel(
            **{
                key: init_flow_node(node, context=context, variables=variables)
                for key, node in root.map.items()
            }
        )
    elif isinstance(root, list):
        nodes = [
            init_flow_node(node, context=context, variables=variables) for node in root
        ]
        return init_sequence(steps=nodes)
    else:
        raise Exception("Invalid flow type: " + str(type(root)))
