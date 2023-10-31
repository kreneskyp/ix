import itertools
import logging
import time
from collections import defaultdict
from typing import Callable, Any, List

from ix.chains.loaders.context import IxContext
from langchain.chains import SequentialChain
from langchain.chains.base import Chain as LangchainChain

from ix.chains.loaders.prompts import load_prompt
from ix.chains.loaders.templates import NodeTemplate
from ix.chains.models import NodeType, ChainNode, ChainEdge
from ix.secrets.models import Secret
from ix.utils.config import format_config
from ix.utils.importlib import import_class

import_node_class = import_class


logger = logging.getLogger(__name__)


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


def get_sequence_inputs(sequence: List[LangchainChain]) -> List[str]:
    """Aggregate all inputs for a list of chains"""
    input_variables = set()
    output_variables = set()
    for sequence_chain in sequence:
        # Intermediate outputs are excluded from input_variables.
        # Filter out any inputs that are already in the output variables
        filtered_inputs = set(sequence_chain.input_keys) - output_variables
        input_variables.update(filtered_inputs)
        output_variables.update(sequence_chain.output_keys)
    return list(input_variables)


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
    node: ChainNode, context: IxContext, root=True, variables=None, as_template=False
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
    properties = node.incoming_edges.filter(relation="PROP").order_by("key")
    for group in itertools.groupby(properties, lambda x: x.key):
        key, edges = group
        node_group = [edge.source for edge in edges]
        logger.debug(f"Loading property key={key} node_group={node_group}")

        # choose the type the incoming connection is processed as. If the source node
        # will be converted to another type, use the as_type defined on the connection
        # this allows a single property loader to encapsulate any necessary conversions.
        # e.g. retriever converting Vectorstore.
        connector = node_type.connectors_as_dict[key]
        as_type = connector.get("as_type", None) or node_group[0].node_type.type
        connector_is_template = connector.get("template", False)

        if node_group[0].node_type.type in {"chain", "agent"}:
            # load a sequence of linked nodes into a children property
            # this supports loading as a list of chains or auto-SequentialChain
            first_instance = load_node(
                node_group[0],
                context,
                root=False,
                variables=variables,
                as_template=connector_is_template,
            )
            sequence = load_sequence(node_group[0], first_instance, context)
            if connector.get("auto_sequence", True):
                input_variables = get_sequence_inputs(sequence)
                config[key] = SequentialChain(
                    chains=sequence, input_variables=input_variables
                )
            else:
                config[key] = sequence
        elif property_loader := get_property_loader(as_type):
            # load type specific config options. This is generally for loading
            # ix specific features into the config dict
            logger.debug(f"Loading with property loader for type={node_type.type}")
            config[key] = property_loader(node_group, context)
        else:
            # default recursive loading
            if connector.get("multiple", False):
                config[key] = [
                    prop_node.load(context, root=False) for prop_node in node_group
                ]
            else:
                if len(node_group) > 1:
                    raise ValueError(f"Multiple values for {key} not allowed")
                config[key] = load_node(
                    node_group[0],
                    context,
                    root=False,
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

    if node_type.type in {"chain"} and root:
        # Linked chains but no parent indicates the possible first node in an
        # implicit SequentialChain. Traverse the sequence and create a
        # SequentialChain if there is more than one node in the sequence.
        sequential_nodes = load_sequence(node, instance, context)
        if len(sequential_nodes) > 1:
            input_variables = get_sequence_inputs(sequential_nodes)
            return SequentialChain(
                chains=sequential_nodes, input_variables=input_variables
            )

    return instance


def load_sequence(
    first_node: ChainNode,
    first_instance: LangchainChain,
    context: IxContext,
) -> List[LangchainChain]:
    """
    Load a sequence of nodes.
    """
    sequential_nodes = [first_instance]

    # handle linked nodes
    # for now only a single outgoing link is supported
    outgoing_link = None
    try:
        outgoing_link = first_node.outgoing_edges.select_related("target").get(
            relation="LINK"
        )
    except ChainEdge.DoesNotExist:
        pass

    # traverse the sequence
    while outgoing_link:
        next_instance = outgoing_link.target.load(context, root=False)
        sequential_nodes.append(next_instance)
        try:
            outgoing_link = outgoing_link.target.outgoing_edges.select_related(
                "target"
            ).get(relation="LINK")
        except ChainEdge.DoesNotExist:
            outgoing_link = None

    return sequential_nodes
