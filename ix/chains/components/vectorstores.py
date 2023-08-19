from typing import Any, List

from asgiref.sync import sync_to_async
from langchain.callbacks.manager import AsyncCallbackManagerForRetrieverRun
from langchain.schema import Document
from langchain.vectorstores import Redis
from langchain.vectorstores.redis import RedisVectorStoreRetriever


class AsyncRedisVectorStoreRetriever(RedisVectorStoreRetriever):
    async def _aget_relevant_documents(
        self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> List[Document]:
        return await sync_to_async(self._get_relevant_documents)(
            query, run_manager=run_manager
        )


class AsyncRedisVectorstore(Redis):
    """Extension of Langchain Redis vectorstore implementation to add async support"""

    def as_retriever(self, **kwargs: Any) -> AsyncRedisVectorStoreRetriever:
        tags = kwargs.pop("tags", None) or []
        tags.extend(self._get_retriever_tags())
        return AsyncRedisVectorStoreRetriever(vectorstore=self, **kwargs, tags=tags)
