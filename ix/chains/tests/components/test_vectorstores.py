from typing import List

import pytest
from asgiref.sync import sync_to_async
from langchain.schema.vectorstore import VectorStore
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents import Document

from ix.chains.fixture_src.vectorstores import (
    CHROMA_CLASS_PATH,
)
from ix.chains.tests.test_config_loader import (
    EMBEDDINGS,
)
from ix.conftest import aload_chain
from ix.runnable.vectorstore import (
    AddTexts,
    AddTextsInput,
    AddDocuments,
    DeleteVectors,
    AddImages,
)

TEST_TEXTS = [
    "def foo1():\n    print('hello world foo1')",
    "def foo2():\n    print('hello world foo2')",
    "def bar3():\n    print('hello world bar3')",
    "def bar4():\n    print('hello world bar4')",
    "def bar5():\n    print('hello world bar5')",
]

TEXT_KWARGS = {
    "texts": TEST_TEXTS,
    "ids": ["foo1", "foo2", "bar3", "bar4", "bar5"],
    "metadatas": [{"foo": "bar"}] * len(TEST_TEXTS),
}


TEST_DOCUMENTS = [
    Document(page_content=text, metadata={"foo": 1}) for text in TEST_TEXTS
]


class VectorStoreTestMixin:
    """Test loading retrieval components.

    This is a test of loading mechanism for the various retrieval components.
    It is not an exhaustive test that all retrieval components work as expected.
    The tests verify that any special loading logic for the components is working.
    """

    CLASS = None
    CONFIG = None

    async def cleanup_vectorstore(self, vectorstore: VectorStore, ids: List[str]):
        if ids:
            if type(vectorstore).adelete != VectorStore.adelete:
                await vectorstore.adelete(ids)
            else:
                await sync_to_async(vectorstore.delete)(ids)
        vectorstore.delete_collection()

    async def test_load_vectorstore(self, aload_chain, mock_openai_embeddings):
        vectorstore: VectorStore = await aload_chain(self.CONFIG)
        assert isinstance(vectorstore, self.CLASS)

        ids = await vectorstore.aadd_texts(**TEXT_KWARGS)
        try:
            results = await vectorstore.asearch("foo", "similarity")
            assert len(results) == 4
            assert results[0].metadata["foo"] == "bar"
        finally:
            await self.cleanup_vectorstore(vectorstore, ids)

    async def test_add_text(self, aload_chain, mock_openai_embeddings):
        vectorstore: VectorStore = await aload_chain(self.CONFIG)
        runnable = AddTexts(vectorstore=vectorstore)
        ids = await runnable.ainvoke(input=AddTextsInput(texts=TEST_TEXTS))

        await self.cleanup_vectorstore(vectorstore, ids)
        assert len(ids) == len(TEST_TEXTS)

    async def test_add_delete_documents(self, aload_chain, mock_openai_embeddings):
        vectorstore: VectorStore = await aload_chain(self.CONFIG)
        runnable = AddDocuments(vectorstore=vectorstore)
        ids = await runnable.ainvoke(input=TEST_DOCUMENTS)
        try:
            assert len(ids) == len(TEST_TEXTS)
            delete_runnable = DeleteVectors(vectorstore=vectorstore)
            await delete_runnable.ainvoke(input=ids)
        finally:
            await self.cleanup_vectorstore(vectorstore, ids)


class AddImagesMixin:
    async def test_add_images(self):
        vectorstore: VectorStore = await aload_chain(self.CONFIG)
        runnable = AddImages(vectorstore=vectorstore)
        ids = await runnable.ainvoke(input=TEST_DOCUMENTS)
        try:
            assert len(ids) == len(TEST_TEXTS)
            delete_runnable = DeleteVectors(vectorstore=vectorstore)
            await delete_runnable.ainvoke(input=ids)
        finally:
            await self.cleanup_vectorstore(vectorstore, ids)


@pytest.mark.django_db
class TestChroma(VectorStoreTestMixin):
    """Test Chroma vectorstore component."""

    CLASS = Chroma
    CONFIG = {
        "class_path": CHROMA_CLASS_PATH,
        "config": {
            "embedding_function": EMBEDDINGS,
            "collection_name": "tests",
        },
    }
