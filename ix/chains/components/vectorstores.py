from typing import Any, List, Iterable, Optional

from asgiref.sync import sync_to_async
from langchain.callbacks.manager import AsyncCallbackManagerForRetrieverRun
from langchain.schema import Document
from langchain.schema.vectorstore import VectorStore
from langchain_community.vectorstores.redis.base import RedisVectorStoreRetriever
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores.redis import Redis


class AsyncAddTextsMixin:
    async def aadd_texts(
        self: VectorStore,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
        return await sync_to_async(self.add_texts)(
            texts=texts, metadatas=metadatas, ids=ids, **kwargs
        )


class AsyncGetRelevantDocumentsMixin:
    async def _aget_relevant_documents(
        self: VectorStore,
        query: str,
        *,
        run_manager: AsyncCallbackManagerForRetrieverRun,
    ) -> List[Document]:
        return await sync_to_async(self._get_relevant_documents)(
            query, run_manager=run_manager
        )


class AsyncRedisVectorStoreRetriever(
    AsyncGetRelevantDocumentsMixin, RedisVectorStoreRetriever
):
    pass


class AsyncRedisVectorstore(AsyncAddTextsMixin, Redis):
    """Extension of Langchain Redis vectorstore implementation to add async support"""

    def as_retriever(self, **kwargs: Any) -> AsyncRedisVectorStoreRetriever:
        tags = kwargs.pop("tags", None) or []
        tags.extend(self._get_retriever_tags())
        return AsyncRedisVectorStoreRetriever(vectorstore=self, **kwargs, tags=tags)


class AsyncChromaVectorstore(AsyncAddTextsMixin, Chroma):
    """Extension of Langchain Chroma vectorstore implementation to add async support"""
