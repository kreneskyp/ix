import pytest

from ix.memory.plugin import get_embeddings
from ix.memory.redis import RedisVectorMemory, RedisVectorMemoryOptions


@pytest.fixture(scope="module")
def redis_options() -> RedisVectorMemoryOptions:
    return {
        "redis_host": "redis",
        "redis_port": 6379,
        "redis_password": None,
        "redis_db": 0,
    }


@pytest.mark.skip()
class TestRedisVectorMemory:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, redis_options: RedisVectorMemoryOptions):
        self.index_name = "test_index"
        self.memory = RedisVectorMemory(self.index_name, redis_options)
        self.memory.create_index()
        yield
        self.memory.clear()

    def test_add_vector_and_find_nearest(self):
        # Add vectors to the index
        self.memory.add_vector("key1", "This is a test sentence.")
        self.memory.add_vector("key2", "Another test sentence is here.")
        self.memory.add_vector("key3", "This sentence is not similar to the other two.")

        # Find the nearest vector to a given query
        query = "Yet another test sentence."
        nearest = self.memory.find_nearest(query, num_results=2)

        assert len(nearest) == 2
        assert nearest[0]["key"] == "key2"
        assert nearest[1]["key"] == "key1"

    def test_delete_vector(self):
        self.memory.add_vector("key1", "This is a test sentence.")
        self.memory.add_vector("key2", "Another test sentence is here.")

        self.memory.delete_vector("key1")

        keys = self.memory.redis.keys(f"{self.index_name}:*")
        assert (
            len(keys) == 2
        )  # Only the keys for the "key2" vector and its text should remain

    def test_get_vector(self):
        sentence = "This is a test sentence."
        self.memory.add_vector("key1", sentence)

        vector = get_embeddings(sentence)
        retrieved_vector = self.memory.get_vector("key1")

        assert len(vector) == len(retrieved_vector)
        assert (
            pytest.approx(vector, rel=1e-6) == retrieved_vector
        )  # Compare the vectors considering a small tolerance

    def test_clear_vectors(self):
        self.memory.add_vector("key1", "This is a test sentence.")
        self.memory.add_vector("key2", "Another test sentence is here.")

        self.memory.clear()

        keys = self.memory.redis.keys(f"{self.index_name}:*")
        assert len(keys) == 0  # No keys should remain after clearing the vectors
