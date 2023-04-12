from __future__ import absolute_import

import numpy as np
from typing import List, Optional, TypedDict, Dict, Any
import faiss
from ix.memory.plugin import VectorMemory, IndexKey, NearestResult, get_embeddings
import os


class FaissVectorMemoryPlugin(VectorMemory):
    def __init__(self, index_name: str, dim: int = 768, options: Optional[Dict[str, Any]] = None):
        options = options or {}
        super().__init__(index_name, options)
        self.dim = len(get_embeddings("test"))  # Get the dimension of the embeddings
        #self.index = faiss.IndexFlatL2(self.dim)
        self.normalize_vectors = self.options.get("normalize_vectors", True)
        self.create_index()

    def create_index(self) -> None:
        self.normalize_vectors = self.options.get("normalize_vectors", True)
        dimensions = len(get_embeddings("test"))  # Get the dimension of the embeddings
        self.index = faiss.IndexFlatL2(dimensions)
        self.index = faiss.IndexIDMap(self.index)

    def _add_vector(self, key: IndexKey, vector: List[float], text: str) -> None:
        key = int(key)  # Ensure the key is an integer
        self.index_key_to_text[key] = text
        vector = np.array([vector], dtype=np.float32)
        if self.normalize_vectors:
            faiss.normalize_L2(vector)
        self.index.add_with_ids(vector, np.array([key], dtype=np.int64))

    def get_vector(self, key: IndexKey) -> List[float]:
        key = int(key)  # Ensure the key is an integer
        return self.index.reconstruct(key)

    def find_nearest(self, query_vector: List[float], num_results: int = 1) -> List[NearestResult]:
        query_vector = np.array([query_vector], dtype=np.float32)
        if self.normalize_vectors:
            faiss.normalize_L2(query_vector)
        _, index_keys = self.index.search(query_vector, num_results)

        nearest_results = []
        for key in index_keys.flatten():
            if key != -1:
                vector = self.get_vector(key)
                score = 1 - self.index.search(vector.reshape(1, -1), 1)[0][0][0]
                data = self.index_key_to_text[key]
                nearest_results.append({"key": key, "score": score, "data": data})

        return nearest_results

    def delete_vector(self, key: IndexKey) -> None:
        self.index.remove_ids(np.array([key]))

    def clear_vectors(self) -> None:
        self.index.reset()
