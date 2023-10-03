import pytest
from asgiref.sync import sync_to_async
from langchain.vectorstores import VectorStore
from pydantic import BaseModel

from ix.chains.components.tools import IngestionTool
from ix.chains.fixture_src.tools import INGESTION_TOOL_CLASS_PATH
from ix.chains.loaders.templates import NodeTemplate
from ix.chains.tests.components.test_vectorstores import CHROMA_VECTORSTORE
from ix.chains.tests.test_config_loader import TEST_DOCUMENTS
from ix.chains.tests.test_templates import LOADER_TEMPLATE

INGESTION_TOOL = {
    "class_path": INGESTION_TOOL_CLASS_PATH,
    "config": {
        "vectorstore": CHROMA_VECTORSTORE,
        "loader_template": LOADER_TEMPLATE,
    },
}

NAMED_INGESTION_TOOL = {
    "class_path": INGESTION_TOOL_CLASS_PATH,
    "config": {
        "name": "custom_ingest",
        "description": "custom description",
        "vectorstore": CHROMA_VECTORSTORE,
        "loader_template": LOADER_TEMPLATE,
    },
}


class What(BaseModel):
    PATH: str


@pytest.mark.django_db
class TestIngestionTool:
    async def test_load(self, aload_chain):
        component = await aload_chain(INGESTION_TOOL)
        assert isinstance(component, IngestionTool)
        assert component.name == "ingest"
        assert component.description == "Ingest data into a vectorstore"
        assert component.args_schema is not None

        # assert connectors loaded
        assert isinstance(component.vectorstore, VectorStore)
        assert isinstance(component.loader_template, NodeTemplate)

        # validate args_schema works as expected
        args_schema = await sync_to_async(component.loader_template.get_args_schema)()
        assert args_schema.schema() == {
            "title": "DynamicArgsSchema",
            "type": "object",
            "properties": {"PATH": {"title": "Path", "type": "string"}},
            "required": ["PATH"],
        }
        assert args_schema.parse_obj(dict(PATH=str(TEST_DOCUMENTS))).dict() == {
            "PATH": str(TEST_DOCUMENTS)
        }

    async def test_load_override_name_and_description(self, aload_chain):
        component = await aload_chain(NAMED_INGESTION_TOOL)
        assert isinstance(component, IngestionTool)
        assert component.name == "custom_ingest"
        assert component.description == "custom description"

    async def test_ainvoke(self, aload_chain, mock_openai_embeddings):
        component = await aload_chain(INGESTION_TOOL)
        result = await component.ainvoke(input=dict(PATH=str(TEST_DOCUMENTS)))

        component.vectorstore.delete(result["document_ids"])
        component.vectorstore.delete_collection()
