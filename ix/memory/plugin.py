import openai
from typing import List, Optional, Dict, Any, Union, TypedDict

IndexKey = Union[int, str]


class NearestResult(TypedDict):
    key: str
    score: float
    data: str


def get_embeddings(text: str) -> List[float]:
    response = openai.Embedding.create(input=[text], model="text-embedding-ada-002")
    return response["data"][0]["embedding"]


class VectorMemory:
    def __init__(self, index_name: str, options: Optional[Dict[str, Any]] = None):
        self.index_name = index_name
        self.options = options or {}

    def create_index(self) -> None:
        raise NotImplementedError

    def add_vector(self, key: IndexKey, text: str) -> None:
        vector = get_embeddings(text)
        self._add_vector(key, vector, text)

    def _add_vector(self, key: IndexKey, vector: List[float], text: str) -> None:
        raise NotImplementedError

    def get_vector(self, key: IndexKey) -> List[float]:
        raise NotImplementedError

    def find_nearest(
        self, query: str, num_results: int = 1
    ) -> List[NearestResult]:
        raise NotImplementedError

    def delete_vector(self, key: IndexKey) -> None:
        raise NotImplementedError

    def clear_vectors(self) -> None:
        raise NotImplementedError
