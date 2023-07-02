import itertools
import logging
import time
from typing import Callable, Any, List

from langchain.chains import SequentialChain
from langchain.chains.base import Chain as LangchainChain

from ix.agents.callback_manager import IxCallbackManager
from ix.chains.loaders.prompts import load_prompt
from ix.chains.models import NodeType, ChainNode, ChainEdge
from ix.utils.importlib import import_class

import_node_class = import_class


logger = logging.getLogger(__name__)


def get_node_loader(name: str) -> Callable:
    """
    Get a node config loader by node type
    """
    from ix.chains.loaders.memory import load_memory_config
    from ix.chains.loaders.memory import load_chat_memory_backend_config

    return {
        "memory": load_memory_config,
        "memory_backend": load_chat_memory_backend_config,
        "prompt": load_prompt,
    }.get(name, None)


def get_property_loader(name: str) -> Callable:
    from ix.chains.loaders.memory import load_memory_property

    return {
        "memory": load_memory_property,
    }.get(name, None)


def get_sequence_inputs(sequence: List[LangchainChain]) -> List[str]:
    """Aggregate all inputs for a list of chains"""
    input_variables = set()
    for sequence_chain in sequence:
        input_variables.update(sequence_chain.input_keys)
    return list(input_variables)


def load_node(node: ChainNode, callback_manager: IxCallbackManager, parent=None) -> Any:
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

    # resolve secrets and settings
    # TODO: implement resolve secrets from vault and settings from vocabulary
    #       neither of these subsystems are implemented yet. For now load all
    #       values as text from config dict

    # load type specific config options. This is generally for loading
    # ix specific features into the config dict
    if node_loader := get_node_loader(node_type.type):
        logger.debug(
            f"Loading config with node config loader for type={node_type.type}"
        )
        config = node_loader(node, callback_manager)

    # prepare properties for loading. Properties should be grouped by key.
    properties = node.incoming_edges.filter(relation="PROP").order_by("key")
    for group in itertools.groupby(properties, lambda x: x.key):
        key, edges = group
        node_group = [edge.source for edge in edges]
        logger.debug(f"Loading property key={key} node_group={node_group}")

        if node_group[0].node_type.type == "chain":
            # load a sequence of linked nodes into a children property
            # this supports loading as an list of chains or auto-SequentialChain
            first_instance = load_node(node_group[0], callback_manager, parent=node)
            sequence = load_sequence(node_group[0], first_instance, callback_manager)
            connector = node_type.connectors_as_dict[key]
            if connector.get("auto_sequence", True):
                input_variables = get_sequence_inputs(sequence)
                config[key] = SequentialChain(
                    chains=sequence, input_variables=input_variables
                )
            else:
                config[key] = sequence
        elif property_loader := get_property_loader(node_group[0].node_type.type):
            # load type specific config options. This is generally for loading
            # ix specific features into the config dict
            logger.debug(f"Loading with property loader for type={node_type.type}")
            config[key] = property_loader(node_group, callback_manager)
        else:
            # default recursive loading
            if node_type.connectors_as_dict[key].get("multiple", False):
                config[key] = [
                    prop_node.load(callback_manager) for prop_node in node_group
                ]
            else:
                if len(node_group) > 1:
                    raise ValueError(f"Multiple values for {key} not allowed")
                config[key] = load_node(node_group[0], callback_manager)

    node_class = import_node_class(node.class_path)

    if node_type.type in {"chain", "agent"}:
        config["callback_manager"] = callback_manager

    instance = node_class(**config)
    logger.debug(f"Loaded node class={node.class_path} in {time.time() - start_time}s")

    if node_type == "chain" and not parent:
        # Linked chains but no parent indicates the possible first node in an
        # implicit SequentialChain. Traverse the sequence and create a
        # SequentialChain if there is more than one node in the sequence.
        sequential_nodes = load_sequence(node, instance)
        if len(sequential_nodes) > 1:
            input_variables = get_sequence_inputs(sequential_nodes)
            return SequentialChain(
                chains=sequential_nodes, input_variables=input_variables
            )

    return instance


def load_sequence(
    first_node: ChainNode,
    first_instance: LangchainChain,
    callback_manager: IxCallbackManager,
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
        next_instance = outgoing_link.target.load(callback_manager)
        sequential_nodes.append(next_instance)
        try:
            outgoing_link = outgoing_link.target.outgoing_edges.select_related(
                "target"
            ).get(relation="LINK")
        except ChainEdge.DoesNotExist:
            outgoing_link = None

    return sequential_nodes
