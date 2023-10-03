from typing import get_type_hints

import pytest
import pytest_asyncio
from asgiref.sync import sync_to_async
from langchain.document_loaders.base import BaseLoader
from langchain.schema import BaseRetriever
from langchain.text_splitter import TextSplitter
from pydantic import BaseModel

from ix.chains.fixture_src.document_loaders import GENERIC_LOADER_CLASS_PATH
from ix.chains.fixture_src.text_splitter import RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH
from ix.chains.loaders.templates import NodeTemplate
from ix.chains.loaders.text_splitter import TextSplitterShim
from ix.chains.models import ChainNode
from ix.chains.tests.test_config_loader import TEST_DOCUMENTS, LANGUAGE_PARSER
from ix.task_log.tests.fake import afake_chain, fake_chain

DOCUMENT_LOADER = {
    "class_path": GENERIC_LOADER_CLASS_PATH,
    "config": {"path": "{PATH}", "suffixes": [".py"], "parser": LANGUAGE_PARSER},
}


TEXT_SPLITTER = {
    "class_path": RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH,
    "config": {"language": "python", "document_loader": DOCUMENT_LOADER},
}

LOADER_TEMPLATE = TEXT_SPLITTER


@pytest_asyncio.fixture
async def aloader_template(anode_types, aix_context) -> NodeTemplate:
    chain = await afake_chain()
    chain_node = await sync_to_async(ChainNode.objects.create_from_config)(
        chain, TEXT_SPLITTER
    )
    assert isinstance(chain_node, ChainNode)
    template = NodeTemplate(node=chain_node, context=aix_context)
    return template


@pytest.fixture()
def loader_template(node_types, ix_context) -> NodeTemplate:
    chain = fake_chain()
    chain_node = ChainNode.objects.create_from_config(chain, TEXT_SPLITTER)
    assert isinstance(chain_node, ChainNode)
    template = NodeTemplate(node=chain_node, context=ix_context)
    return template


class Foo(BaseModel):
    bar: str


@pytest.mark.django_db
class TestNodeTemplate:
    def test_init(self, loader_template):
        """Smoke tests for creating object"""
        assert loader_template is not None
        assert isinstance(loader_template, NodeTemplate)

    async def test_ainit(self, aloader_template):
        """Smoke tests for creating object"""
        assert aloader_template is not None
        assert isinstance(aloader_template, NodeTemplate)

    def test_format(self, loader_template):
        """Test loading the component with aformat"""
        component = loader_template.format({"PATH": str(TEST_DOCUMENTS)})
        assert isinstance(component, TextSplitterShim)
        assert isinstance(component.document_loader, BaseLoader)
        assert isinstance(component.text_splitter, TextSplitter)

        # assert path property is correctly set
        assert str(component.document_loader.blob_loader.path) == str(TEST_DOCUMENTS)

        # non-exhaustive test of document loading to show component is usable
        documents = component.document_loader.load()
        sources = {doc.metadata["source"] for doc in documents}
        expected_sources = {
            str(TEST_DOCUMENTS / "foo.py"),
            str(TEST_DOCUMENTS / "bar.py"),
        }
        assert sources == expected_sources

    async def test_aformat(self, aloader_template):
        """Test loading the component with aformat"""
        component = await aloader_template.aformat({"PATH": str(TEST_DOCUMENTS)})
        assert isinstance(component, TextSplitterShim)
        assert isinstance(component.document_loader, BaseLoader)
        assert isinstance(component.text_splitter, TextSplitter)

        # assert path property is correctly set
        assert str(component.document_loader.blob_loader.path) == str(TEST_DOCUMENTS)

        # non-exhaustive test of document loading to show component is usable
        documents = component.document_loader.load()
        sources = {doc.metadata["source"] for doc in documents}
        expected_sources = {
            str(TEST_DOCUMENTS / "foo.py"),
            str(TEST_DOCUMENTS / "bar.py"),
        }
        assert sources == expected_sources

    async def test_get_variables(self, aloader_template):
        variables = await aloader_template.get_variables()
        assert isinstance(variables, set)

    def test_args_schema(self, loader_template):
        model = loader_template.get_args_schema()
        assert issubclass(model, BaseModel)
        assert "PATH" in model.__fields__
        assert model.schema() == {
            "title": "DynamicArgsSchema",
            "type": "object",
            "properties": {"PATH": {"title": "Path", "type": "string"}},
            "required": ["PATH"],
        }
        assert model(PATH=str(TEST_DOCUMENTS)).dict() == {"PATH": str(TEST_DOCUMENTS)}

    def test_type_hint(self):
        def function_with_type_hint(arg: NodeTemplate[BaseRetriever]) -> None:
            pass

        type_hints = get_type_hints(function_with_type_hint)
        assert "arg" in type_hints
        assert type_hints["arg"].__origin__ == NodeTemplate
        assert type_hints["arg"].__args__[0] == BaseRetriever
