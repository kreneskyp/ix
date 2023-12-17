import pytest
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents import Document

from ix.chains.fixture_src.text_splitter import RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH
from ix.chains.loaders.context import IxContext
from ix.chains.tests.fake import afake_chain_node, afake_chain
from ix.runnable.transformer import RunTransformer


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

        chain = await afake_chain()
        node = afake_chain_node(
            chain=chain,
            config={
                "class_path": RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH,
                "config": ""
            },
            root=True,
        )


        runnable = await chain.aload_chain(context=aix_context)

        assert isinstance(runnable, RunTransformer)

        result = await runnable.ainvoke(input=documents)

        assert result == [
            Document(page_content="A", metadata={"test": 123}),
            Document(page_content="test", metadata={"test": 123}),
            Document(page_content="document", metadata={"test": 123}),
        ]