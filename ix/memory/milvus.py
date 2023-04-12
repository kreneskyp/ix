from __future__ import absolute_import
import milvus
from typing import List, Optional, Dict, Any, Union, TypedDict

from ix.memory.plugin import VectorMemory, NearestResult, IndexKey


class MilvusVectorMemory(VectorMemory):
    def __init__(self, index_name: str, options: Optional[Dict[str, Any]] = None):
        super().__init__(index_name, options)
        self.milvus_client = milvus.Milvus()
        self.create_index()

    def create_index(self) -> None:
        collection_params = {
            "collection_name": self.index_name,
            "dimension": 768,
            "index_file_size": 1024,
            "metric_type": milvus.MetricType.IP,
        }
        self.milvus_client.create_collection(collection_params)

    def _add_vector(self, key: IndexKey, vector: List[float], text: str) -> None:
        status, ids = self.milvus_client.insert(
            collection_name=self.index_name, records=[vector], ids=[key]
        )
        if not status.OK():
            raise RuntimeError("Failed to insert vector: {}".format(status.message))

    def get_vector(self, key: IndexKey) -> List[float]:
        status, vectors = self.milvus_client.get_entity_by_id(self.index_name, ids=[key])
        if not status.OK():
            raise RuntimeError("Failed to get vector: {}".format(status.message))
        return vectors[0]

    def find_nearest(
        self, query_vector: List[float], num_results: int = 1
    ) -> List[NearestResult]:
        search_params = {"nprobe": 10}
        status, results = self.milvus_client.search(
            collection_name=self.index_name,
            query_records=[query_vector],
            top_k=num_results,
            params=search_params,
            metric_type=milvus.MetricType.IP,
        )
        if not status.OK():
            raise RuntimeError("Failed to find nearest vector: {}".format(status.message))

        nearest_results = [
            {"key": result.id, "score": result.distance, "data": result.entity}
            for result in results[0]
        ]
        return nearest_results

    def delete_vector(self, key: IndexKey) -> None:
        status = self.milvus_client.delete_entity_by_id(self.index_name, ids=[key])
        if not status.OK():
            raise RuntimeError("Failed to delete vector: {}".format(status.message))

    def clear_vectors(self) -> None:
        status = self.milvus_client.drop_collection(self.index_name)
        if not status.OK():
            raise RuntimeError("Failed to clear vectors: {}".format(status.message))
        self.create_index()
