from ix.chains.fixture_src.common import VERBOSE
from ix.chains.fixture_src.targets import (
    MEMORY_TARGET,
    SEQUENCE_CHAINS_TARGET,
    VECTORSTORE_TARGET,
    CHAIN_TARGET,
)

SEQUENCE = {
    "class_path": "langchain.chains.SequentialChain",
    "name": "Sequence",
    "description": "Runs a sequence of chains passing outputs from one to the next.",
    "display_type": "list",
    "type": "chain",
    "child_field": "chains",
    "connectors": [MEMORY_TARGET, SEQUENCE_CHAINS_TARGET],
    "fields": [VERBOSE],
}


MAP_SUBCHAIN = {
    "class_path": "ix.chains.routing.MapSubchain",
    "type": "chain",
    "name": "MapSubchain",
    "description": "Runs a subchain for each item in a list.",
    "display_type": "list",
    "child_field": "chains",
    "connectors": [MEMORY_TARGET, SEQUENCE_CHAINS_TARGET],
    "fields": [
        {
            "name": "input_variables",
            "type": "list",
            "input": "string",
        },
        {
            "name": "map_input",
            "label": "Map Input",
            "type": "string",
        },
        {
            "name": "map_input_to",
            "label": "Map Input To",
            "type": "string",
        },
        {
            "name": "output_key",
            "type": "string",
        },
    ],
}

ROUTING_KEYS_FIELD = {
    "name": "routing_keys",
    "type": "list",
    "input": "string",
    "description": "Keys to use for routing.",
}

EMBEDDING_ROUTER_CHAIN = {
    "class_path": "langchain.chains.router.embedding_router.EmbeddingRouterChain",
    "type": "chain",
    "name": "Embedding Router Chain",
    "description": "Class that uses embeddings to route between options.",
    "connectors": [
        VECTORSTORE_TARGET,
        MEMORY_TARGET,
    ],
    "fields": [ROUTING_KEYS_FIELD, VERBOSE],
}


LLM_ROUTER_CHAIN = {
    "class_path": "langchain.chains.router.llm_router.LLMRouterChain",
    "type": "chain",
    "name": "LLM Router Chain",
    "description": "A router chain that uses an LLM chain to perform routing.",
    "connectors": [
        CHAIN_TARGET,
        MEMORY_TARGET,
    ],
    "fields": [VERBOSE],
}


MULTI_ROUTE_CHAIN = {
    "class_path": "langchain.chains.router.base.MultiRouteChain",
    "type": "chain",
    "name": "Multi-Route Chain",
    "description": "Use a single chain to route an input to one of multiple candidate chains.",
    "connectors": [
        {
            "key": "router_chain",
            "type": "target",
            "source_type": "chain",
        },
        {
            "key": "destination_chains",
            "type": "target",
            "source_type": "chain",
            "multiple": True,
        },
        {
            "key": "default_chain",
            "type": "target",
            "source_type": "chain",
        },
    ],
    "fields": [
        {
            "name": "silent_errors",
            "type": "boolean",
            "default": False,
            "description": "If True, use default_chain when an invalid destination name is provided",
        }
    ],
}
