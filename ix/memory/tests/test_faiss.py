import pytest
from ix.memory.faiss import FaissVectorMemoryPlugin


@pytest.mark.skip()
class TestFaissVectorMemoryPlugin:
    @pytest.fixture(scope="class", autouse=True)
    def faiss_memory(self):
        index_name = "test_faiss_memory"
        memory = FaissVectorMemoryPlugin(index_name)
        yield memory
        memory.clear_vectors()

    def test_add_and_get_vector(self, faiss_memory):
        key = "1"
        text = "This is a test message."
        faiss_memory.add_vector(key, text)
        vector = faiss_memory.get_vector(key)
        assert vector is not None
        assert len(vector) > 0

    def test_find_nearest(self, faiss_memory):
        key1 = "1"
        text1 = "This is a test message."
        key2 = "2"
        text2 = "Another test message."
        faiss_memory.add_vector(key1, text1)
        faiss_memory.add_vector(key2, text2)

        results = faiss_memory.find_nearest("test message", num_results=2)
        assert len(results) == 2
        assert results[0]["id"] == key1
        assert results[1]["id"] == key2

    def test_delete_vector(self, faiss_memory):
        key = "3"
        text = "This message will be deleted."
        faiss_memory.add_vector(key, text)
        vector = faiss_memory.get_vector(key)
        assert vector is not None

        faiss_memory.delete_vector(key)
        with pytest.raises(AssertionError):
            faiss_memory.get_vector(key)
