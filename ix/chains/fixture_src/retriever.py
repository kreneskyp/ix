from langchain.vectorstores.base import VectorStoreRetriever

from ix.api.chains.types import NodeTypeField
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
    + NodeTypeField.get_fields_from_model(
        VectorStoreRetriever,
        include=[
            "search_type",
        ],
    ),
}

RETRIEVERS = [
    VECTORSTORE_RETRIEVER,
]

__all__ = ["RETRIEVERS", "VECTORSTORE_RETRIEVER_CLASS_PATH"]
