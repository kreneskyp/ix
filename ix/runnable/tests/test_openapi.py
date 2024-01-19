import httpx
import pytest
import pytest_asyncio
from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1

from ix.api.chains.types import ChainQueryPage, Chain as ChainPydantic, CreateChain
from ix.chains.tests.fake import afake_chain
from ix.data.models import Schema
from ix.runnable.openapi import RunOpenAPIRequest
from ix.server.fast_api import app
from ix.utils.tests.mock_schema import LIST_PATH, SERVER, DETAIL_PATH, SCHEMA


@pytest.fixture
def mock_httpx(mocker):
    """Mock httpx.AsyncClient to use FastAPI app as transport."""
    original_async_client = httpx.AsyncClient

    def async_client_wrapper(*args, **kwargs):
        kwargs["app"] = app
        return original_async_client(*args, **kwargs)

    mocker.patch("httpx.AsyncClient", side_effect=async_client_wrapper)


@pytest.fixture
def schema():
    return Schema.objects.create(
        name="IX Test Schema",
        type="openapi",
        description="Subset of IX schema for testing",
        value=SCHEMA,
    )


@pytest_asyncio.fixture
async def aschema():
    return await Schema.objects.acreate(
        name="IX Test Schema",
        type="openapi",
        description="Subset of IX schema for testing",
        value=SCHEMA,
    )


@pytest.mark.django_db
class TestRunOpenAPIRequest:
    def test_input_query_args(self, schema):
        """Test that component can be initialized"""
        runnable = RunOpenAPIRequest(
            schema_id=schema.id, path=LIST_PATH, method="get", server=SERVER
        )
        assert issubclass(runnable.get_input_schema(), (BaseModel, BaseModelV1))
        assert runnable.get_input_schema().model_json_schema() == {
            "$defs": {
                "DynamicModel": {
                    "properties": {
                        "is_agent": {
                            "anyOf": [{"type": "boolean"}, {"type": "null"}],
                            "default": None,
                            "title": "Is Agent",
                        },
                        "limit": {
                            "anyOf": [{"type": "integer"}, {"type": "null"}],
                            "default": 10,
                            "title": "Limit",
                        },
                        "offset": {
                            "anyOf": [{"type": "integer"}, {"type": "null"}],
                            "default": 0,
                            "title": "Offset",
                        },
                        "search": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "default": None,
                            "title": "Search",
                        },
                    },
                    "title": "DynamicModel",
                    "type": "object",
                }
            },
            "properties": {
                "query": {
                    "anyOf": [{"$ref": "#/$defs/DynamicModel"}, {"type": "null"}],
                    "default": None,
                }
            },
            "title": "DynamicModel",
            "type": "object",
        }

    def test_input_with_path_args(self, schema):
        """Test that component can be initialized"""
        runnable = RunOpenAPIRequest(
            schema_id=schema.id, path=DETAIL_PATH, method="get", server=SERVER
        )
        input_schema = runnable.get_input_schema()
        assert issubclass(input_schema, (BaseModel, BaseModelV1))
        assert input_schema.model_json_schema() == {
            "$defs": {
                "DynamicModel": {
                    "properties": {"chain_id": {"title": "Chain Id", "type": "string"}},
                    "required": ["chain_id"],
                    "title": "DynamicModel",
                    "type": "object",
                }
            },
            "properties": {
                "args": {
                    "anyOf": [{"$ref": "#/$defs/DynamicModel"}, {"type": "null"}],
                    "default": None,
                }
            },
            "title": "DynamicModel",
            "type": "object",
        }

    def test_input_with_body_args(self, schema):
        """Test that component can be initialized"""
        runnable = RunOpenAPIRequest(
            schema_id=schema.id, path=LIST_PATH, method="post", server=SERVER
        )

        input_schema = runnable.get_input_schema()
        assert issubclass(input_schema, (BaseModel, BaseModelV1))
        assert input_schema.model_json_schema() == {
            "$defs": {
                "CreateChain": {
                    "properties": {
                        "alias": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "default": None,
                            "title": "Alias",
                        },
                        "description": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "title": "Description",
                        },
                        "is_agent": {
                            "anyOf": [{"type": "boolean"}, {"type": "null"}],
                            "default": False,
                            "title": "Is Agent",
                        },
                        "name": {"title": "Name", "type": "string"},
                    },
                    "required": ["name", "description"],
                    "title": "CreateChain",
                    "type": "object",
                }
            },
            "properties": {"body": {"$ref": "#/$defs/CreateChain"}},
            "required": ["body"],
            "title": "DynamicModel",
            "type": "object",
        }

    async def test_ainvoke_get_list(self, auser, aschema, mock_httpx):
        await afake_chain()
        runnable = RunOpenAPIRequest(
            schema_id=aschema.id,
            path=LIST_PATH,
            method="get",
            server=SERVER,
            headers={},
        )
        output = await runnable.ainvoke(input={})
        page = ChainQueryPage.model_validate(output)
        assert page.count >= 1

    async def test_ainvoke_get_detail(self, aschema, auser, mock_httpx):
        chain = await afake_chain(is_agent=False)
        runnable = RunOpenAPIRequest(
            schema_id=aschema.id, path=DETAIL_PATH, method="get", server=SERVER
        )
        output = await runnable.ainvoke(input={"path": {"chain_id": str(chain.id)}})
        assert ChainPydantic.model_validate(output).id == chain.id

    async def test_ainvoke_post_list(self, aschema, auser, mock_httpx):
        runnable = RunOpenAPIRequest(
            schema_id=aschema.id, path=LIST_PATH, method="post", server=SERVER
        )

        data = CreateChain(
            name="Test Chain",
            description="Test Chain Description",
            is_agent=False,
        )
        output = await runnable.ainvoke(input={"body": data.model_dump()})
        chain = ChainPydantic.model_validate(output)

        assert chain.name == data.name
        assert chain.description == data.description
        assert chain.is_agent == data.is_agent
