import json

import pytest
from pydantic import BaseModel

from ix.chains.components.tools import IngestionTool
from ix.chains.fixture_src.text_splitter import RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH
from ix.chains.fixture_src.tools import INGESTION_TOOL_CLASS_PATH
from ix.chains.fixture_src.vectorstores import CHROMA_CLASS_PATH
from ix.chains.loaders.templates import NodeTemplate
from ix.chains.tests.test_config_loader import TEST_DOCUMENTS, EMBEDDINGS
from ix.chains.tests.test_templates import LOADER_TEMPLATE

CHROMA_TEMPLATE = {
    "class_path": CHROMA_CLASS_PATH,
    "config": {
        "embedding": EMBEDDINGS,
        "collection_name": "{COLLECTION_NAME}",
    },
}

INGESTION_TOOL = {
    "class_path": INGESTION_TOOL_CLASS_PATH,
    "config": {
        "vectorstore": CHROMA_TEMPLATE,
        "loader_template": LOADER_TEMPLATE,
    },
}

NAMED_INGESTION_TOOL = {
    "class_path": INGESTION_TOOL_CLASS_PATH,
    "config": {
        "name": "custom_ingest",
        "description": "custom description",
        "vectorstore": CHROMA_TEMPLATE,
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
        assert isinstance(component.vectorstore, NodeTemplate)
        assert component.vectorstore.node.class_path == CHROMA_CLASS_PATH
        assert isinstance(component.loader_template, NodeTemplate)
        assert (
            component.loader_template.node.class_path
            == RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH
        )

        # validate args_schema works as expected
        expected = {
            "properties": {
                "COLLECTION_NAME": {"title": "Collection Name", "type": "string"},
                "PATH": {"title": "Path", "type": "string"},
            },
            "required": ["COLLECTION_NAME", "PATH"],
            "title": "NodeTemplateSchema",
            "type": "object",
        }
        expected_json = json.dumps(expected, sort_keys=True)
        schema = component.args_schema.schema()
        schema["required"].sort()
        assert json.dumps(schema, sort_keys=True) == expected_json

        args = dict(PATH=str(TEST_DOCUMENTS), COLLECTION_NAME="test_collection")
        assert component.args_schema.parse_obj(args).dict() == {
            "PATH": str(TEST_DOCUMENTS),
            "COLLECTION_NAME": "test_collection",
        }

    async def test_load_override_name_and_description(self, aload_chain):
        component = await aload_chain(NAMED_INGESTION_TOOL)
        assert isinstance(component, IngestionTool)
        assert component.name == "custom_ingest"
        assert component.description == "custom description"

    async def test_ainvoke(self, aload_chain, mock_openai_embeddings):
        component = await aload_chain(INGESTION_TOOL)
        args = dict(PATH=str(TEST_DOCUMENTS), COLLECTION_NAME="test_collection")
        try:
            result = await component.ainvoke(input=args)
        finally:
            vectorstore = await component.vectorstore.aformat(args)
            vectorstore.delete(result["document_ids"])
            vectorstore.delete_collection()
