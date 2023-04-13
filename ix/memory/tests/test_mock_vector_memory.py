import pytest

from ix.memory.plugin import NearestResult
from ix.memory.tests.mock_vector_memory import MockMemory


@pytest.fixture
def mock_memory():
    memory = MockMemory(index_name="test_index")
    return memory


def test_add_vector(mock_memory):
    mock_memory.add_vector(key="key1", text="text1")
    mock_memory.add_vector(key="key2", text="text2")
    mock_memory.add_vector(key="key3", text="text3")
    assert mock_memory.get_vector("key1") == [0.1, 0.2, 0.3]
    assert mock_memory.get_vector("key2") == [0.1, 0.2, 0.3]
    assert mock_memory.get_vector("key3") == [0.1, 0.2, 0.3]
    assert mock_memory.memory["key1"] == {
        "data": "text1",
        "key": "key1",
        "score": 0.99,
        "vector": [0.1, 0.2, 0.3],
    }
    assert mock_memory.memory["key2"] == {
        "data": "text2",
        "key": "key2",
        "score": 0.98,
        "vector": [0.1, 0.2, 0.3],
    }
    assert mock_memory.memory["key3"] == {
        "data": "text3",
        "key": "key3",
        "score": 0.97,
        "vector": [0.1, 0.2, 0.3],
    }


def test_find_nearest(mock_memory):
    mock_memory.add_vector(key="key1", text="text1")
    mock_memory.add_vector(key="key2", text="text2")
    mock_memory.add_vector(key="key3", text="text3")

    nearest = mock_memory.find_nearest(query="text4", num_results=2)
    expected = [
        NearestResult(key="key1", score=0.99, data="text1"),
        NearestResult(key="key2", score=0.98, data="text2"),
    ]
    assert nearest == expected


def test_delete_vector(mock_memory):
    mock_memory.add_vector(key="key1", text="text1")
    mock_memory.delete_vector(key="key1")
    with pytest.raises(KeyError):
        mock_memory.get_vector("key1")


def test_clear_vectors(mock_memory):
    mock_memory.add_vector(key="key1", text="text1")
    mock_memory.add_vector(key="key2", text="text2")
    mock_memory.clear_vectors()
    with pytest.raises(KeyError):
        mock_memory.get_vector("key1")
    with pytest.raises(KeyError):
        mock_memory.get_vector("key2")
