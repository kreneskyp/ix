import pytest
from ix.memory.pinecone import PineconeMemory


@pytest.fixture(scope="module")
def pinecone_memory():
    index_name = "pytest-memory"
    memory = PineconeMemory(index_name)
    yield memory
    memory.clear()


@pytest.mark.skip(reason="Costs money to test this!")
class TestPineconeMemory:
    def test_add_and_get_vector(self, pinecone_memory):
        key = "1"
        text = "This is a test message."
        pinecone_memory.add_vector(key, text)
        response = pinecone_memory.get_vector(key)

        assert response is not None
        assert response["metadata"]["data"] == text
        assert len(response["values"]) > 0

    def test_find_nearest(self, pinecone_memory):
        key1 = "1"
        text1 = "This is a test message."
        key2 = "2"
        text2 = "Another test message."
        pinecone_memory.add_vector(key1, text1)
        pinecone_memory.add_vector(key2, text2)

        results = pinecone_memory.find_nearest("test message", num_results=2)
        assert len(results) == 2
        assert results[1]["key"] == key1
        assert results[1]["data"] == text1
        assert results[0]["key"] == key2
        assert results[0]["data"] == text2
        assert results[0]["score"] > results[1]["score"]

    def test_delete_vector(self, pinecone_memory):
        key = "3"
        text = "This message will be deleted."
        pinecone_memory.add_vector(key, text)
        vector = pinecone_memory.get_vector(key)
        assert vector is not None

        pinecone_memory.delete_vector(key)
        with pytest.raises(KeyError):
            pinecone_memory.get_vector(key)
