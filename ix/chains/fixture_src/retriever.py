from langchain.retrievers import MultiQueryRetriever
from langchain.vectorstores.base import VectorStoreRetriever

from ix.chains.fixture_src.targets import (
    RETRIEVER_TARGET,
    LLM_TARGET,
    PROMPT_TARGET,
)
from ix.api.components.types import NodeTypeField
from ix.chains.fixture_src.targets import VECTORSTORE_TARGET

VECTORSTORE_RETRIEVER_CLASS_PATH = "langchain.vectorstores.base.VectorStoreRetriever"
VECTORSTORE_RETRIEVER = {
    "class_path": VECTORSTORE_RETRIEVER_CLASS_PATH,
    "type": "retriever",
    "name": "VectorStoreRetriever",
    "description": "Default vector",
    "connectors": [VECTORSTORE_TARGET],
    "fields": [
        {
            "name": "allowed_search_types",
            "type": "list",
            "required": True,
            "default": ["similarity", "similarity_score_threshold", "mmr"],
        }
    ]
    + NodeTypeField.get_fields(
        VectorStoreRetriever,
        include=[
            "search_type",
        ],
    ),
}


MULTI_QUERY_RETRIEVER_CLASS_PATH = (
    "libs.langchain.langchain.retrievers.multi_query.MultiQueryRetriever.from_llm"
)
MULTI_QUERY_RETRIEVER = {
    "class_path": MULTI_QUERY_RETRIEVER_CLASS_PATH,
    "type": "retriever",
    "name": "MultiQueryRetriever",
    "description": "MultiQueryRetriever",
    "connectors": [RETRIEVER_TARGET, LLM_TARGET, PROMPT_TARGET],
    "fields": [] + NodeTypeField.get_fields(MultiQueryRetriever, include=["parse_key"]),
}


RETRIEVERS = [VECTORSTORE_RETRIEVER, MULTI_QUERY_RETRIEVER]

__all__ = [
    "RETRIEVERS",
    "VECTORSTORE_RETRIEVER_CLASS_PATH",
    "MULTI_QUERY_RETRIEVER_CLASS_PATH",
]
