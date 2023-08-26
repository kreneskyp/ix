import pytest
from langchain.embeddings import CacheBackedEmbeddings

from ix.chains.fixture_src.embeddings import EMBEDDINGS_CACHE_CLASS_PATH
from ix.chains.fixture_src.storage import REDIS_STORE_CLASS_PATH
from ix.chains.tests.test_config_loader import EMBEDDINGS

REDIS_STORE = {
    "class_path": REDIS_STORE_CLASS_PATH,
    "config": {
        "redis_url": "redis://localhost:6379/0",
        "ttl": 3600,
        "namespace": "redis_store_tests",
    },
}

EMBEDDINGS_CACHE = {
    "class_path": EMBEDDINGS_CACHE_CLASS_PATH,
    "config": {
        "underlying_embeddings": EMBEDDINGS,
        "document_embedding_store": REDIS_STORE,
    },
}


@pytest.mark.django_db
class TestEmbeddingsCache:
    async def test_load(self, aload_chain):
        component = await aload_chain(EMBEDDINGS_CACHE)
        assert isinstance(component, CacheBackedEmbeddings)
