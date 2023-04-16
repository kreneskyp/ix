from typing import Dict, List, Optional, Any
from collections import OrderedDict

from ix.memory.plugin import VectorMemory, IndexKey, NearestResult


class MockMemory(VectorMemory):
    """
    `MockMemory` is an implementation of the `VectorMemory` abstract class that stores vector and text data in memory
    using an ordered dictionary, and calculates a mocked cosine similarity value based on the order of insertion.

    Usage:
    1. Instantiate the `MockMemory` class with an index name and an optional options dictionary:
        `memory = MockMemory(index_name="my_index")`
    2. Call the `add_vector` method to add a vector and its corresponding text to the memory:
        `memory.add_vector(key="my_key", text="my_text")`
    3. Call the `find_nearest` method to find the nearest vectors to a query vector:
        `nearest = memory.find_nearest(query_vector=[0.1, 0.2, 0.3])`
    4. Call the `delete_vector` method to delete a vector and its corresponding text from the memory:
        `memory.delete_vector(key="my_key")`
    5. Call the `clear_vectors` method to remove all vectors and their corresponding text from the memory:
        `memory.clear_vectors()`
    """

    def __init__(self, index_name: str, options: Optional[Dict[str, Any]] = None):
        super().__init__(index_name, options)
        self.memory = OrderedDict()

    def create_index(self) -> None:
        pass

    def _add_vector(self, key: IndexKey, vector: List[float], text: str) -> None:
        mock_score = 0.99 - (0.01 * len(self.memory))
        self.memory[key] = {
            "key": key,
            "data": text,
            "score": mock_score,
            "vector": [0.1, 0.2, 0.3],
        }

    def get_vector(self, key: IndexKey) -> List[float]:
        return self.memory[key]["vector"]

    def find_nearest(self, query: str, num_results: int = 1) -> List[NearestResult]:
        nearest = list(self.memory.values())
        nearest.sort(key=lambda item: item["score"], reverse=True)
        formatted = [
            NearestResult(key=item["key"], score=item["score"], data=item["data"])
            for item in nearest[:num_results]
        ]
        return formatted

    def delete_vector(self, key: IndexKey) -> None:
        del self.memory[key]

    def clear(self) -> None:
        self.memory.clear()
