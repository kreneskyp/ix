import pytest
from ix.memory.milvus import MilvusVectorMemory

INDEX_NAME = "test_index"


@pytest.fixture(scope="module")
def vector_memory():
    vm = MilvusVectorMemory(INDEX_NAME)
    yield vm
    vm.clear_vectors()


@pytest.mark.skip()
class TestMilvusVectorMemory:
    def test_create_index_and_add_vector(self, vector_memory):
        vector_memory.add_vector(1, "test text")
        vector = vector_memory.get_vector(1)
        assert len(vector) == 768

    def test_find_nearest(self, vector_memory):
        vector_memory.add_vector(1, "apple")
        vector_memory.add_vector(2, "banana")
        vector_memory.add_vector(3, "orange")

        nearest_results = vector_memory.find_nearest("fruit", num_results=2)

        assert len(nearest_results) == 2
        assert {result["key"] for result in nearest_results} == {1, 2, 3} - {3}

    def test_delete_vector(self, vector_memory):
        vector_memory.add_vector(1, "test text")
        vector_memory.delete_vector(1)

        with pytest.raises(RuntimeError, match="Failed to get vector"):
            vector_memory.get_vector(1)

    def test_clear_vectors(self, vector_memory):
        vector_memory.add_vector(1, "apple")
        vector_memory.add_vector(2, "banana")
        vector_memory.add_vector(3, "orange")

        vector_memory.clear_vectors()

        with pytest.raises(RuntimeError, match="Failed to get vector"):
            vector_memory.get_vector(1)
