from __future__ import absolute_import
import redis
import numpy as np
from typing import List, Optional, Dict, Any, Union, TypedDict

from ix.memory.plugin import VectorMemory, IndexKey, NearestResult, get_embeddings


class RedisVectorMemoryOptions(TypedDict):
    redis_host: str
    redis_port: int
    redis_password: Optional[str]
    redis_db: int


class RedisVectorMemory(VectorMemory):
    def __init__(
        self,
        index_name: str,
        options: Optional[RedisVectorMemoryOptions] = None
    ):
        super().__init__(index_name, options)
        self.redis = redis.StrictRedis(
            host=options["redis_host"],
            port=options["redis_port"],
            password=options["redis_password"],
            db=options["redis_db"]
        )

    def _vector_key(self, key: IndexKey) -> str:
        return f"{self.index_name}:vector:{key}"

    def _text_key(self, key: IndexKey) -> str:
        return f"{self.index_name}:text:{key}"

    def create_index(self) -> None:
        pass

    def _add_vector(self, key: IndexKey, vector: List[float], text: str) -> None:
        vector_key = self._vector_key(key)
        text_key = self._text_key(key)
        vector_str = ",".join(str(v) for v in vector)
        with self.redis.pipeline() as pipe:
            pipe.set(vector_key, vector_str)
            pipe.set(text_key, text)
            pipe.execute()

    def get_vector(self, key: IndexKey) -> List[float]:
        vector_key = self._vector_key(key)
        vector_str = self.redis.get(vector_key)
        return [float(x) for x in vector_str.decode().split(",")] if vector_str else None

    def find_nearest(
        self, query_string: str, num_results: int = 1
    ) -> List[NearestResult]:
        query_vector = get_embeddings(query_string)
        query_np = np.array(query_vector)
        keys = self.redis.keys(f"{self.index_name}:vector:*")
        scores = []

        for key in keys:
            vector_str = self.redis.get(key).decode()
            vector = np.array([float(x) for x in vector_str.split(",")])
            cosine_similarity = np.dot(query_np, vector) / (np.linalg.norm(query_np) * np.linalg.norm(vector))
            index_key = key.decode().split(":")[-1]
            scores.append((index_key, cosine_similarity))

        scores.sort(key=lambda x: x[1], reverse=True)
        nearest_results = []
        for key, score in scores[:num_results]:
            text = self.redis.get(self._text_key(key)).decode()
            nearest_results.append({"key": key, "score": score, "data": text})

        return nearest_results

    def delete_vector(self, key: IndexKey) -> None:
        vector_key = self._vector_key(key)
        text_key = self._text_key(key)
        with self.redis.pipeline() as pipe:
            pipe.delete(vector_key)
            pipe.delete(text_key)
            pipe.execute()

    def clear_vectors(self) -> None:
        keys = self.redis.keys(f"{self.index_name}:*")
        if keys:
            self.redis.delete(*keys)
