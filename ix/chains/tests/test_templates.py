from typing import get_type_hints

import pytest
import pytest_asyncio
from asgiref.sync import sync_to_async
from langchain.schema import BaseRetriever
from pydantic import BaseModel

from ix.chains.components.vectorstores import AsyncChromaVectorstore
from ix.chains.fixture_src.vectorstores import CHROMA_CLASS_PATH
from ix.chains.loaders.templates import NodeTemplate
from ix.chains.models import ChainNode
from ix.chains.tests.mock_configs import EMBEDDINGS
from ix.task_log.tests.fake import afake_chain, fake_chain


CHROMA_TEMPLATE = {
    "class_path": CHROMA_CLASS_PATH,
    "config": {
        "embedding_function": EMBEDDINGS,
        "collection_name": "{COLLECTION_NAME}",
    },
}

NODE_TEMPLATE = CHROMA_TEMPLATE


@pytest_asyncio.fixture
async def aloader_template(anode_types, aix_context) -> NodeTemplate:
    chain = await afake_chain()
    chain_node = await sync_to_async(ChainNode.objects.create_from_config)(
        chain, NODE_TEMPLATE
    )
    assert isinstance(chain_node, ChainNode)
    template = NodeTemplate(node=chain_node, context=aix_context)
    return template


@pytest.fixture()
def loader_template(node_types, ix_context) -> NodeTemplate:
    chain = fake_chain()
    chain_node = ChainNode.objects.create_from_config(chain, NODE_TEMPLATE)
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
        component = loader_template.format({"COLLECTION_NAME": "test_collection"})
        assert isinstance(component, AsyncChromaVectorstore)

        # assert property is correctly set
        assert str(component._collection.name) == "test_collection"

    async def test_aformat(self, aloader_template):
        """Test loading the component with aformat"""
        component = await aloader_template.aformat(
            {"COLLECTION_NAME": "test_collection"}
        )
        assert isinstance(component, AsyncChromaVectorstore)

        # assert property is correctly set
        assert str(component._collection.name) == "test_collection"

    def test_get_variables(self, loader_template):
        variables = loader_template.get_variables()
        assert isinstance(variables, set)

    def test_args_schema(self, loader_template):
        model = loader_template.get_args_schema()
        assert issubclass(model, BaseModel)
        assert "COLLECTION_NAME" in model.__fields__
        assert model.model_json_schema() == {
            "title": "NodeTemplateSchema",
            "type": "object",
            "properties": {"COLLECTION_NAME": {"title": "Collection Name"}},
            "required": ["COLLECTION_NAME"],
        }
        assert model(COLLECTION_NAME="test_collection").model_dump() == {
            "COLLECTION_NAME": "test_collection"
        }

    def test_type_hint(self):
        def function_with_type_hint(arg: NodeTemplate[BaseRetriever]) -> None:
            pass

        type_hints = get_type_hints(function_with_type_hint)
        assert "arg" in type_hints
        assert type_hints["arg"].__origin__ == NodeTemplate
        assert type_hints["arg"].__args__[0] == BaseRetriever
