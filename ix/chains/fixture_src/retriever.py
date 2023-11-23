from langchain.retrievers import MultiQueryRetriever

from ix.chains.fixture_src.targets import (
    RETRIEVER_TARGET,
    LLM_TARGET,
    PROMPT_TARGET,
)
from ix.api.components.types import NodeTypeField
from ix.chains.fixture_src.targets import VECTORSTORE_TARGET
from ix.chains.fixture_src.vectorstores import VECTORSTORE_RETRIEVER_FIELDS

VECTORSTORE_RETRIEVER_CLASS_PATH = "langchain.schema.vectorstore.VectorStoreRetriever"
VECTORSTORE_RETRIEVER = {
    "class_path": VECTORSTORE_RETRIEVER_CLASS_PATH,
    "type": "retriever",
    "name": "VectorStoreRetriever",
    "description": "Default vector",
    "connectors": [VECTORSTORE_TARGET],
    "fields": VECTORSTORE_RETRIEVER_FIELDS,
}


MULTI_QUERY_RETRIEVER_CLASS_PATH = (
    "langchain.retrievers.multi_query.MultiQueryRetriever.from_llm"
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
