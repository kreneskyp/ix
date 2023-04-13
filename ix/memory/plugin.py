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
    """
    VectorMemory is a generic interface for creating vector-based memory systems, where
    text data is stored along with its corresponding vector representation. This base class
    provides an abstraction layer that can be implemented with different storage backends,
    such as Redis, Elasticsearch, or other similar data stores.

    The __init__ method of the VectorMemory class expects two arguments: index_name and an
    optional options dictionary. The index_name is a string that uniquely identifies the vector
    index within the chosen backend, allowing multiple indexes to be stored and managed separately.
    The options dictionary is used to pass implementation-specific configuration settings to the
    backend. When implementing a new vector memory system using a specific backend, you should
    define a TypedDict that specifies the expected keys and types of values in the options
    dictionary, providing a clear and well-documented interface for users.

    To implement a new vector memory system using a specific backend, you should create a
    subclass that inherits from the VectorMemory class, and then implement the following methods:

    - create_index(self) -> None:
        This method should create any necessary structures for the vector index in the backend.

    - _add_vector(self, key: IndexKey, vector: List[float], text: str) -> None:
        This method should store the given vector and its corresponding text in the backend using
        the given key. This method is called internally by the `add_vector` method, which converts
        the input text into a vector before passing it to this method.

    - get_vector(self, key: IndexKey) -> List[float]:
        This method should return the vector representation for the given key.

    - find_nearest(self, query: str, num_results: int = 1) -> List[NearestResult]:
        This method should find and return the nearest vectors to the given string, based on
        the similarity metric of choice (e.g., cosine similarity). It should return a list of
        NearestResult dictionaries containing the keys, similarity scores, and text data of the
        nearest vectors.

    - delete_vector(self, key: IndexKey) -> None:
        This method should delete the vector and its corresponding text for the given key.

    - clear_vectors(self) -> None:
        This method should remove all vectors and their corresponding text data from the backend.

    Once these methods are implemented, the new vector memory system can be used with the provided
    methods such as `add_vector`, `find_nearest`, `delete_vector`, and `clear_vectors`.
    """

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

    def find_nearest(self, query: str, num_results: int = 1) -> List[NearestResult]:
        raise NotImplementedError

    def delete_vector(self, key: IndexKey) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError
