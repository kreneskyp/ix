from typing import Callable

import pytest
from langchain.text_splitter import (
    CharacterTextSplitter,
)
from langchain_community.document_loaders.generic import GenericLoader
from langchain_core.documents import Document
from pydantic import BaseModel

from ix.chains.fixture_src.document_loaders import GENERIC_LOADER_CLASS_PATH
from ix.chains.fixture_src.text_splitter import (
    CHARACTER_SPLITTER_CLASS_PATH,
)
from ix.chains.loaders.context import IxContext
from ix.chains.tests.fake import (
    afake_chain_node,
    afake_chain,
    afake_root,
    afake_root_edge,
)
from ix.runnable.ix import IxNode
from ix.runnable.documents import RunTransformer, RunLoader


@pytest.mark.django_db
class TestRunTransformer:
    async def test_ainvoke(self, aix_context: IxContext):
        content = """A\n\ntest\n\ndocument"""
        documents = [Document(page_content=content, metadata={"test": 123})]
        transformer = CharacterTextSplitter(chunk_size=1, chunk_overlap=0)
        transformer = RunTransformer(transformer=transformer)

        result = await transformer.ainvoke(input=documents)

        assert result == [
            Document(page_content="A", metadata={"test": 123}),
            Document(page_content="test", metadata={"test": 123}),
            Document(page_content="document", metadata={"test": 123}),
        ]

    async def test_auto_wrap(self, aix_context: IxContext):
        """Document transformers should be loaded as RunTransformers
        automatically."""

        content = """A\n\ntest\n\ndocument"""
        documents = [Document(page_content=content, metadata={"test": 123})]

        # build chain
        chain = await afake_chain()
        root = await afake_root(chain=chain)
        node = await afake_chain_node(
            chain=chain,
            config={
                "class_path": CHARACTER_SPLITTER_CLASS_PATH,
                "config": dict(chunk_size=1, chunk_overlap=0),
            },
        )
        await afake_root_edge(chain=chain, root=root, target=node)

        # assert runnable
        runnable = await chain.aload_chain(context=aix_context)
        assert isinstance(runnable, IxNode)
        assert isinstance(runnable.child, RunTransformer)
        assert isinstance(runnable.child.transformer, CharacterTextSplitter)

        # assert output
        result = await runnable.ainvoke(input=documents)
        assert result == [
            Document(page_content="A", metadata={"test": 123}),
            Document(page_content="test", metadata={"test": 123}),
            Document(page_content="document", metadata={"test": 123}),
        ]


@pytest.mark.django_db
class TestRunLoader:
    def test_input_type(self):
        """validate the input type dynamically generated for the targeted BaseLoader initializer"""

        initializer = GenericLoader.from_filesystem
        runnable = RunLoader(initializer=initializer, config={})
        input_type = runnable.InputType
        assert issubclass(input_type, BaseModel)

        # validate model parsing
        instance = input_type(
            path="test",
            glob="**/[!.]*",
        )
        assert isinstance(instance, BaseModel)
        assert instance.path == "test"
        assert instance.glob == "**/[!.]*"

        # validate model fields
        assert "path" in input_type.__fields__.keys()
        assert "glob" in input_type.__fields__.keys()

    def test_get_loader(self, mock_filesystem):
        """Test creating the loader from input."""
        mock_filesystem.write_file("test.txt", "this is a test document")
        initializer = GenericLoader.from_filesystem
        runnable = RunLoader(initializer=initializer, config={})
        loader = runnable.get_loader(dict(path=mock_filesystem.workdir, glob="*.txt"))
        assert isinstance(loader, GenericLoader)
        documents = loader.load()
        assert isinstance(documents, list)
        assert len(documents) == 1
        assert isinstance(documents[0], Document)
        assert documents[0].page_content == "this is a test document"

    async def test_ainvoke(self, aix_context: IxContext, mock_filesystem):
        """Test running the component"""
        mock_filesystem.write_file("test.txt", "this is a test document")
        initializer = GenericLoader.from_filesystem
        runnable = RunLoader(
            initializer=initializer,
            config={"path": mock_filesystem.workdir, "glob": "*.txt"},
        )
        result = await runnable.ainvoke(input=[])
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Document)
        assert result[0].page_content == "this is a test document"

    async def test_override_config(self, aix_context: IxContext, mock_filesystem):
        """Input field can override config value."""
        mock_filesystem.write_file("foo.txt", "this is a foo document")
        mock_filesystem.write_file("bar.txt", "this is a bar document")
        initializer = GenericLoader.from_filesystem
        runnable = RunLoader(
            initializer=initializer,
            config={"path": mock_filesystem.workdir, "glob": "foo.txt"},
        )
        result = await runnable.ainvoke(input={"glob": "bar.txt"})
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Document)
        assert result[0].page_content == "this is a bar document"

    async def test_auto_wrap(self, aix_context: IxContext, mock_filesystem):
        """Document loaders should be loaded as RunLoaders automatically."""

        mock_filesystem.write_file("test.txt", "this is a test document")

        # build chain
        chain = await afake_chain()
        root = await afake_root(chain=chain)
        node = await afake_chain_node(
            chain=chain,
            config={
                "class_path": GENERIC_LOADER_CLASS_PATH,
                "config": dict(path=str(mock_filesystem.workdir), glob="*.txt"),
            },
        )
        await afake_root_edge(chain=chain, root=root, target=node)

        # assert runnable
        runnable = await chain.aload_chain(context=aix_context)
        assert isinstance(runnable, IxNode)
        assert isinstance(runnable.child, RunLoader)
        assert isinstance(runnable.child.initializer, Callable)
        assert runnable.child.config == dict(
            path=str(mock_filesystem.workdir), glob="*.txt"
        )

        # assert output
        result = await runnable.ainvoke(input=[])
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Document)
        assert result[0].page_content == "this is a test document"
