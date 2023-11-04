import pytest
from langchain.schema.vectorstore import VectorStore
from langchain.vectorstores import Chroma

from ix.chains.fixture_src.document_loaders import GENERIC_LOADER_CLASS_PATH
from ix.chains.fixture_src.text_splitter import RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH
from ix.chains.fixture_src.vectorstores import (
    CHROMA_CLASS_PATH,
)
from ix.chains.tests.test_config_loader import (
    EMBEDDINGS,
    TEXT_SPLITTER,
    LANGUAGE_PARSER,
)


DOCUMENT_LOADER_EMPTY = {
    "class_path": GENERIC_LOADER_CLASS_PATH,
    "config": {
        "parser": LANGUAGE_PARSER,
        "path": "/var/doesnotexist",
        "suffixes": [".does.not.exist"],
        "glob": "doesnotexist",
    },
}

TEXT_SPLITTER_EMPTY = {
    "class_path": RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH,
    "config": {"language": "python", "document_loader": DOCUMENT_LOADER_EMPTY},
}

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


class VectorStoreTestMixin:
    """Test loading retrieval components.

    This is a test of loading mechanism for the various retrieval components.
    It is not an exhaustive test that all retrieval components work as expected.
    The tests verify that any special loading logic for the components is working.
    """

    CLASS = None
    CONFIG = None
    CONFIG_WITH_DOCUMENTS = None
    CONFIG_WITH_EMPTY_DOCUMENTS = None

    async def test_load_vectorstore(self, aload_chain, mock_openai_embeddings):
        vectorstore: VectorStore = await aload_chain(self.CONFIG)
        assert isinstance(vectorstore, self.CLASS)

        ids = await vectorstore.aadd_texts(**TEXT_KWARGS)
        results = await vectorstore.asearch("foo", "similarity")
        assert len(results) == 4
        assert results[0].metadata["foo"] == "bar"

        vectorstore.delete(ids)
        vectorstore.delete_collection()

    async def test_load_vectorstore_with_document_source(
        self, mock_import_class, aload_chain, mock_openai_embeddings
    ):
        vectorstore: VectorStore = await aload_chain(self.CONFIG_WITH_DOCUMENTS)
        assert isinstance(vectorstore, self.CLASS)

        ids = await vectorstore.aadd_texts(**TEXT_KWARGS)

        results = await vectorstore.asearch("foo", "similarity")
        assert len(results) == 4

        vectorstore.delete(ids)
        vectorstore.delete_collection()

    async def test_load_vectorstore_with_empty_document_source(
        self, aload_chain, mock_openai_embeddings
    ):
        vectorstore: VectorStore = await aload_chain(self.CONFIG_WITH_EMPTY_DOCUMENTS)
        assert isinstance(vectorstore, self.CLASS)

        ids = await vectorstore.aadd_texts(**TEXT_KWARGS)
        results = await vectorstore.asearch("foo", "similarity")
        assert len(results) == 4
        assert results[0].metadata["foo"] == "bar"

        vectorstore.delete(ids)
        vectorstore.delete_collection()


CHROMA_VECTORSTORE_WITH_EMPTY_DOCUMENTS = {
    "class_path": CHROMA_CLASS_PATH,
    "config": {
        "embedding": EMBEDDINGS,
        "documents": TEXT_SPLITTER_EMPTY,
        "collection_name": "tests",
    },
}

CHROMA_VECTORSTORE_WITH_DOCUMENTS = {
    "class_path": CHROMA_CLASS_PATH,
    "config": {
        "embedding": EMBEDDINGS,
        "documents": TEXT_SPLITTER,
        "collection_name": "tests",
    },
}

CHROMA_VECTORSTORE = {
    "class_path": CHROMA_CLASS_PATH,
    "config": {
        "embedding": EMBEDDINGS,
        "collection_name": "tests",
    },
}


@pytest.mark.django_db
class TestChroma(VectorStoreTestMixin):
    """Test Chroma vectorstore component."""

    CLASS = Chroma
    CONFIG = CHROMA_VECTORSTORE
    CONFIG_WITH_DOCUMENTS = CHROMA_VECTORSTORE_WITH_DOCUMENTS
    CONFIG_WITH_EMPTY_DOCUMENTS = CHROMA_VECTORSTORE_WITH_EMPTY_DOCUMENTS
