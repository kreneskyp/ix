import logging
import os
from typing import List, TypedDict, Optional
import pinecone
from ix.memory.plugin import VectorMemory, IndexKey, NearestResult, get_embeddings


logger = logging.getLogger(__name__)


class PineconeOptions(TypedDict, total=False):
    metric: str
    pod_type: str
    dimension: int


class PineconeMemory(VectorMemory):
    def __init__(self, index_name: str, options: Optional[PineconeOptions] = None):
        super().__init__(index_name, options)
        self.pinecone_api_key = os.environ["PINECONE_API_KEY"]
        self.pinecone_env = os.environ["PINECONE_ENV"]

        if self.pinecone_api_key is None:
            raise Exception("PINECONE_API_KEY must be set in environment")
        if self.pinecone_env is None:
            raise Exception("PINECONE_ENV must be set in environment")

        pinecone.init(api_key=self.pinecone_api_key, environment=self.pinecone_env)
        self.create_index()

    def create_index(self):
        options = {
            "metric": "cosine",
            "pod_type": "p1",
            "dimension": 1536,
        }
        options.update(self.options)
        if self.index_name not in pinecone.list_indexes():
            self.index = pinecone.create_index(self.index_name, **options)
        else:
            self.index = pinecone.Index(self.index_name)

    def _add_vector(self, key: IndexKey, vector: List[float], data: str):
        logger.info("Inserting key={key} data={data}")
        self.index.upsert([(key, vector, {"data": data})])

    def get_vector(self, key: IndexKey) -> List[float]:
        return self.index.fetch([key])["vectors"][key]

    def find_nearest(
        self, query_text: str, num_results: int = 1
    ) -> List[NearestResult]:
        query_embedding = get_embeddings(query_text)
        results = self.index.query(
            query_embedding, top_k=num_results, include_metadata=True
        )
        sorted_results = sorted(results.matches, key=lambda x: x.score, reverse=True)

        # Retrieve text for each embedding and add it to the results
        sorted_results_with_text = []

        for item in sorted_results:
            sorted_results_with_text.append(
                {
                    "key": item.id,
                    "score": item.score,
                    "data": item.metadata["data"],
                }
            )

        return sorted_results_with_text

    def delete_vector(self, key: IndexKey):
        self.index.delete(key)

    def clear_vectors(self):
        self.index.delete(deleteAll=True)
