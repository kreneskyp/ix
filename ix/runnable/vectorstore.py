from typing import Dict, Optional, Any, List, Sequence

from asgiref.sync import sync_to_async
from langchain.schema.runnable import RunnableSerializable, RunnableConfig
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from pydantic import BaseModel


class AddTextsInput(BaseModel):
    texts: List[str]
    metadata: Optional[Dict[str, Any]] = None


class AddTexts(RunnableSerializable[AddTextsInput, List[str]]):
    """Add texts with metadata to a vectorstore"""

    vectorstore: VectorStore

    class Config:
        arbitrary_types_allowed = True

    def invoke(
        self,
        input: AddTextsInput,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> List[str]:
        if isinstance(input, dict):
            input = AddTextsInput(**input)
        return self.vectorstore.add_texts(**input.model_dump())

    async def ainvoke(
        self,
        input: AddTextsInput,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> List[str]:
        if isinstance(input, dict):
            input = AddTextsInput(**input)
        return await self.vectorstore.aadd_texts(**input.model_dump())


class AddDocuments(RunnableSerializable[Sequence[Document], List[str]]):
    """Add documents to a vectorstore"""

    vectorstore: VectorStore

    class Config:
        arbitrary_types_allowed = True

    def invoke(
        self,
        input: Sequence[Document],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> List[str]:
        return self.vector_store.add_documents(documents=input)

    async def ainvoke(
        self,
        input: Sequence[Document],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> List[str]:
        return await self.vectorstore.aadd_documents(documents=input)


class AddImageInput(BaseModel):
    uris: List[str]
    metadatas: Optional[List[dict]] = (None,)
    ids: Optional[List[str]] = (None,)


class AddImages(RunnableSerializable[AddImageInput, List[str]]):
    """Add images to a vectorstore"""

    vectorstore: VectorStore

    class Config:
        arbitrary_types_allowed = True

    def invoke(
        self,
        input: Document,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> str:
        if not hasattr(self.vectorstore, "add_images"):
            raise ValueError("This vectorstore does not support adding images")
        return self.vectorstore.add_images(document=input)

    async def ainvoke(
        self,
        input: Document,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> str:
        if not hasattr(self.vectorstore, "aadd_images"):
            return await self.vectorstore.aadd_image(document=input)
        elif hasattr(self.vectorstore, "add_images"):
            return await sync_to_async(self.vectorstore.add_images)(document=input)
        else:
            raise ValueError("This vectorstore does not support adding images")


class DeleteVectors(RunnableSerializable[AddTextsInput, List[str]]):
    vectorstore: VectorStore

    class Config:
        arbitrary_types_allowed = True

    def invoke(
        self,
        input: List[str],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Optional[bool]:
        return self.vectorstore.delete(ids=input)

    async def ainvoke(
        self, input: List[str], config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> Optional[bool]:
        if type(self.vectorstore).adelete == VectorStore.adelete:
            return await sync_to_async(self.vectorstore.delete)(ids=input)
        else:
            return await self.vectorstore.adelete(ids=input)
