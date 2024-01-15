import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores.redis.base import RedisVectorStoreRetriever
from langchain_core.vectorstores import VectorStoreRetriever

from ix.api.components.types import NodeTypeField, NodeType, Connector
from ix.chains.fixture_src.targets import (
    EMBEDDINGS_TARGET,
    DOCUMENTS_TARGET,
    VECTORSTORE_TARGET,
)
from django.conf import settings

VECTORSTORE_CONNECTORS = [EMBEDDINGS_TARGET, DOCUMENTS_TARGET]

# common fields for the generic retriever
VECTORSTORE_RETRIEVER_FIELDS = [
    {
        "name": "allowed_search_types",
        "type": "list",
        "required": True,
        "default": ["similarity", "similarity_score_threshold", "mmr"],
    }
] + NodeTypeField.get_fields(
    VectorStoreRetriever,
    include=["search_type", "search_kwargs"],
)


REDIS_VECTORSTORE_CLASS_PATH = "ix.chains.components.vectorstores.AsyncRedisVectorstore"

REDIS_VECTORSTORE_RETRIEVER_FIELDS = (
    VECTORSTORE_RETRIEVER_FIELDS
    + NodeTypeField.get_fields(
        RedisVectorStoreRetriever,
        include=[
            "k",
            "score_threshold",
        ],
    )
)

REDIS_VECTORSTORE = {
    "class_path": REDIS_VECTORSTORE_CLASS_PATH,
    "type": "vectorstore",
    "name": "Redis Vector Store",
    "description": "Redis Vector Store",
    "connectors": VECTORSTORE_CONNECTORS,
    "fields": [
        {
            "name": "redis_url",
            "type": "string",
            "description": "URL of the Redis server",
            "default": "redis://redis:6379/0",
            "style": {"width": "100%"},
        },
        {
            "name": "index_name",
            "type": "string",
            "description": "Name of the index in the Redis",
        },
        {
            "name": "content_key",
            "type": "string",
            "default": "content",
            "description": "Key for storing content",
        },
        {
            "name": "metadata_key",
            "type": "string",
            "default": "metadata",
            "description": "Key for storing metadata",
        },
        {
            "name": "vector_key",
            "type": "string",
            "default": "content_vector",
            "description": "Key for storing vectors",
        },
    ]
    + REDIS_VECTORSTORE_RETRIEVER_FIELDS,
}

CHROMA_CLASS_PATH = "ix.chains.components.vectorstores.AsyncChromaVectorstore"
CHROMA = {
    "class_path": CHROMA_CLASS_PATH,
    "type": "vectorstore",
    "name": "Chroma",
    "description": "Chroma vector database",
    "connectors": [
        Connector(key="embedding_function", type="target", source_type="embeddings"),
        DOCUMENTS_TARGET,
    ],
    "fields": NodeTypeField.get_fields(
        Chroma.__init__,
        include=[
            "collection_name",
            "persist_directory",
        ],
        field_options={
            "persist_directory": {
                "default": "./chroma",
            }
        },
    )
    + NodeTypeField.get_fields(
        chromadb.config.Settings,
        parent="client_settings",
        include=[
            "chroma_server_host",
            "chroma_server_http_port",
            "chroma_server_grpc_port",
            "chroma_server_ssl_enabled",
            "anonymized_telemetry",
            "allow_reset",
        ],
        field_options={
            "chroma_server_host": {
                "label": "Server Host",
                "default": settings.DOCKER_HOST_IP,
            },
            "chroma_server_http_port": {"label": "HTTP Port", "default": "8020"},
            "chroma_server_grpc_port": {
                "label": "GRPC Port",
            },
            "Chroma_server_ssl_enabled": {
                "label": "SSL Enabled",
            },
        },
    )
    + VECTORSTORE_RETRIEVER_FIELDS,
    "field_groups": {
        "client_settings": {
            "class_path": "chromadb.config.Settings",
        }
    },
}


def get_vectorstore_retriever_fieldnames(class_path: str):
    fields = {REDIS_VECTORSTORE_CLASS_PATH: REDIS_VECTORSTORE_RETRIEVER_FIELDS}.get(
        class_path, VECTORSTORE_RETRIEVER_FIELDS
    )
    return [field["name"] for field in fields]


ADD_TEXTS_CLASS_PATH = "ix.runnable.vectorstore.AddTexts"
ADD_DOCUMENTS_CLASS_PATH = "ix.runnable.vectorstore.AddDocuments"
ADD_IMAGES_CLASS_PATH = "ix.runnable.vectorstore.AddImages"
DELETE_VECTORS_CLASS_PATH = "ix.runnable.vectorstore.DeleteVectors"

ADD_TEXTS = NodeType(
    class_path=ADD_TEXTS_CLASS_PATH,
    type="chain",
    name="Add Texts",
    description="Add texts with metadata to a vectorstore",
    connectors=[VECTORSTORE_TARGET],
)

ADD_DOCUMENTS = NodeType(
    class_path=ADD_DOCUMENTS_CLASS_PATH,
    type="chain",
    name="Add Documents",
    description="Add documents to a vectorstore",
    connectors=[VECTORSTORE_TARGET],
)

ADD_IMAGES = NodeType(
    class_path=ADD_IMAGES_CLASS_PATH,
    type="chain",
    name="Add Images",
    description="Add images to a vectorstore",
    connectors=[VECTORSTORE_TARGET],
)

DELETE_VECTORS = NodeType(
    class_path=DELETE_VECTORS_CLASS_PATH,
    type="chain",
    name="Delete Vectors",
    description="Delete vectors from a vectorstore",
    connectors=[VECTORSTORE_TARGET],
)

RUNNABLES = [
    ADD_TEXTS,
    ADD_DOCUMENTS,
    ADD_IMAGES,
    DELETE_VECTORS,
]


VECTORSTORES = RUNNABLES + [REDIS_VECTORSTORE, CHROMA]
__all__ = ["VECTORSTORES"]
