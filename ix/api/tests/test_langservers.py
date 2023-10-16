import httpx
import pytest
from ix.api.langservers.types import LangServerConfig, RemoteRunnableConfig
from ix.ix_users.tests.mixins import OwnershipTestsMixin
from ix.langservers.models import LangServer
from ix.server.fast_api import app
from httpx import AsyncClient

from ix.langservers.tests.fake import (
    FakeConfigSchema,
    FakeInputSchema,
    FakeOutputSchema,
    afake_langserver,
)
from ix.langservers.tests.mock_langserve import mock_openapi_schema

URL = "http://langserve"

LANGSERVER_DATA = {
    "name": "Test LangServer",
    "description": "This is a test LangServer",
    "url": URL,
    "routes": [
        RemoteRunnableConfig(
            name="test_route",
            input_schema=FakeInputSchema.schema(),
            output_schema=FakeOutputSchema.schema(),
            config_schema=FakeConfigSchema(),
        ).dict()
    ],
    "headers": {"mock": "test"},
}


@pytest.mark.django_db
class TestLangServers:
    async def test_create_langserver(self, auser):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/langservers/", json=LANGSERVER_DATA)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we created the LangServer
        assert result["name"] == "Test LangServer"
        assert result["description"] == "This is a test LangServer"
        assert result["url"] == URL

    @pytest.mark.respx(base_url="http://test")
    async def test_import_langserver(self, auser, respx_mock):
        langserver_data = {
            "url": URL,
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            # mock all the api endpoints we need to import the langserver
            respx_mock.get(f"{URL}/openapi.json").mock(
                return_value=httpx.Response(200, json=mock_openapi_schema)
            )
            respx_mock.get(f"{URL}/jokes/input_schema").mock(
                return_value=httpx.Response(200, json=FakeInputSchema().schema())
            )
            respx_mock.get(f"{URL}/jokes/output_schema").mock(
                return_value=httpx.Response(200, json=FakeOutputSchema().schema())
            )
            respx_mock.get(f"{URL}/jokes/config_schema").mock(
                return_value=httpx.Response(200, json=FakeConfigSchema().schema())
            )
            respx_mock.get(f"{URL}/tales/input_schema").mock(
                return_value=httpx.Response(200, json=FakeInputSchema().schema())
            )
            respx_mock.get(f"{URL}/tales/output_schema").mock(
                return_value=httpx.Response(200, json=FakeOutputSchema().schema())
            )
            respx_mock.get(f"{URL}/tales/config_schema").mock(
                return_value=httpx.Response(200, json=FakeConfigSchema().schema())
            )

            response = await ac.post("/import_langserver/", json=langserver_data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we imported the LangServer
        assert result["name"] == "PirateServe"
        assert result["description"] == "A simple api for pirate jokes"
        assert result["url"] == URL

        # assert routes
        assert len(result["routes"]) == 2
        assert result["routes"][0]["name"] == "jokes"
        assert result["routes"][1]["name"] == "tales"
        assert result["routes"][0]["input_schema"] == FakeInputSchema.schema()
        assert result["routes"][0]["output_schema"] == FakeOutputSchema.schema()
        assert result["routes"][0]["config_schema"] == FakeConfigSchema.schema()
        assert result["routes"][1]["input_schema"] == FakeInputSchema.schema()
        assert result["routes"][1]["output_schema"] == FakeOutputSchema.schema()
        assert result["routes"][1]["config_schema"] == FakeConfigSchema.schema()

    async def test_get_langserver(self, auser):
        langserver = await afake_langserver()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/langservers/{langserver.id}")

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we got the correct LangServer
        assert result["name"] == langserver.name
        assert result["description"] == langserver.description
        assert result["url"] == langserver.url

    async def test_get_langservers(self, auser):
        langserver_1 = await afake_langserver(name="LangServer 1")
        langserver_2 = await afake_langserver(name="LangServer 2")

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/langservers/")

        assert response.status_code == 200, response.content
        page = response.json()

        # Check that we got a list of LangServers
        objects = page["objects"]
        assert len(objects) >= 2
        langserver_ids = [langserver["id"] for langserver in objects]
        assert str(langserver_1.id) in langserver_ids
        assert str(langserver_2.id) in langserver_ids

    async def test_update_langservers(self, auser):
        langserver = await afake_langserver()

        data = LangServerConfig(
            name="Updated LangServer",
            description="This is an updated LangServer",
            url="http://updated-langserver.com",
            routes=[
                RemoteRunnableConfig(
                    name="test_route_updated",
                    input_schema=FakeInputSchema(),
                    output_schema=FakeOutputSchema(),
                    config_schema=FakeConfigSchema(),
                )
            ],
        ).dict()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/langservers/{langserver.id}", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we updated the LangServer
        assert result["name"] == "Updated LangServer"
        assert result["description"] == "This is an updated LangServer"
        assert result["url"] == "http://updated-langserver.com"

    async def test_delete_langserver(self, auser):
        langserver = await afake_langserver()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/langservers/{langserver.id}")

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we deleted the LangServer
        assert result["id"] == str(langserver.id)
        assert not await LangServer.objects.filter(pk=langserver.id).aexists()


@pytest.mark.django_db
class TestLangServerOwnership(OwnershipTestsMixin):
    object_type = "langservers"

    async def setup_object(self, **kwargs):
        return await afake_langserver(**kwargs)

    async def get_create_data(self):
        return LANGSERVER_DATA

    async def get_update_data(self, instance):
        data = LANGSERVER_DATA.copy()
        data["name"] = "Updated LangServer"
        data["description"] = "Updated LangServer Description"
        data["url"] = "http://updated-langserver.com"
        return data
