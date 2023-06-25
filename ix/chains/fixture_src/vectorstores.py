from ix.chains.fixture_src.targets import EMBEDDINGS_TARGET

REDIS_VECTORSTORE = {
    "class_path": "langchain.vectorstores.Redis",
    "type": "vector_store",
    "name": "Redis Vector Store",
    "description": "Redis Vector Store",
    "connectors": [EMBEDDINGS_TARGET],
    "fields": [
        {
            "name": "redis_url",
            "type": "string",
            "description": "URL of the Redis server",
            "default": "redis://redis:6379/0",
            "width": "100%",
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
    ],
}
