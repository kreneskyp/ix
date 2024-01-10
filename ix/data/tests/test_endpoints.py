from ix.data.models import Schema, Data
from ix.data.tests.fake import afake_schema, FakeSchema
from ix.ix_users.tests.mixins import OwnershipTestsMixin
from ix.server.fast_api import app
import pytest
from uuid import uuid4
from httpx import AsyncClient


@pytest.mark.django_db
class TestSchema:
    async def test_create_schema(self, auser):
        data = {
            "name": "Test Schema",
            "type": "json",
            "description": "A test schema",
            "value": {},
            "meta": {},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/schemas/", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we created the schema
        assert result["name"] == "Test Schema"
        assert result["type"] == "json"

    async def test_get_schema(self, auser):
        schema = await Schema.objects.acreate(
            name="Test Schema", type="json", description="A test schema"
        )

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/schemas/{schema.id}")

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we got the correct schema detail
        assert result["id"] == str(schema.id)
        assert result["name"] == "Test Schema"

    async def test_update_schema(self, auser):
        schema = await Schema.objects.acreate(
            name="Test Schema", type="json", description="A test schema"
        )
        update_data = {
            "name": "Updated Schema",
            "type": "json",
            "description": "An updated test schema",
            "value": {},
            "meta": {},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/schemas/{schema.id}", json=update_data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we updated the schema
        assert result["name"] == "Updated Schema"

    async def test_delete_schema(self, auser):
        schema = await Schema.objects.acreate(
            name="Test Schema", type="json", description="A test schema"
        )

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/schemas/{schema.id}")

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["id"] == str(schema.id)

        # Ensure the schema is deleted
        assert not await Schema.objects.filter(id=schema.id).aexists()

    async def test_schema_not_found(self, auser):
        non_existent_schema_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/schemas/{non_existent_schema_id}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Schema not found"


@pytest.mark.django_db
class TestSchemaOwnership(OwnershipTestsMixin):
    object_type = "schemas"

    async def setup_object(self, **kwargs):
        return await Schema.objects.acreate(
            name="Test Schema", type="json", description="A test schema", **kwargs
        )

    async def get_create_data(self):
        return {
            "name": "New Schema",
            "type": "json",
            "description": "New schema",
            "value": {},
            "meta": {},
        }

    async def get_update_data(self, instance):
        return {
            "name": "Updated Schema",
            "type": "json",
            "description": "Updated schema",
            "value": {},
            "meta": {},
        }


@pytest.mark.django_db
class TestData:
    async def test_create_data(self, auser):
        schema = await afake_schema()
        datum = FakeSchema().model_dump()
        data = {
            "name": "Test Data",
            "description": "A test data",
            "schema_id": str(schema.id),
            "value": datum,
            "meta": {},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/data/", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we created the data
        assert result["name"] == "Test Data"
        assert result["schema_id"] == str(schema.id)
        assert result["value"] == datum
        assert result["meta"] == {}

    async def test_get_data(self, auser):
        schema = await afake_schema()
        datum = FakeSchema().model_dump()

        data_obj = await Data.objects.acreate(
            name="Test Data", schema=schema, description="A test data", value=datum
        )
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/data/{data_obj.id}")

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we got the correct data detail
        assert result["id"] == str(data_obj.id)
        assert result["name"] == "Test Data"
        assert result["schema_id"] == str(schema.id)
        assert result["value"] == datum
        assert result["meta"] == {}

    async def test_update_data(self, auser):
        schema = await afake_schema()
        data_obj = await Data.objects.acreate(
            name="Test Data", schema=schema, description="A test data"
        )
        datum = FakeSchema().model_dump()
        update_data = {
            "name": "Updated Data",
            "description": "An updated test data",
            "schema_id": str(schema.id),
            "value": datum,
            "meta": {},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/data/{data_obj.id}", json=update_data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we updated the data
        assert result["name"] == "Updated Data"
        assert result["value"] == datum

    async def test_delete_data(self, auser):
        schema = await afake_schema()
        data_obj = await Data.objects.acreate(
            name="Test Data", schema=schema, description="A test data"
        )

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/data/{data_obj.id}")

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["id"] == str(data_obj.id)

        # Ensure the data is deleted
        assert not await Data.objects.filter(id=data_obj.id).aexists()

    async def test_data_not_found(self, auser):
        non_existent_data_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/data/{non_existent_data_id}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Data not found"


@pytest.mark.django_db
class TestDataOwnership(OwnershipTestsMixin):
    object_type = "data"

    async def setup_object(self, **kwargs):
        schema = await afake_schema()
        return await Data.objects.acreate(
            name="Test Data", schema=schema, description="A test data", **kwargs
        )

    async def get_create_data(self):
        schema = await afake_schema()
        return {
            "name": "New Data",
            "description": "New data",
            "schema_id": str(schema.id),
            "value": {},
            "meta": {},
        }

    async def get_update_data(self, instance):
        return {
            "name": "Updated Data",
            "description": "Updated data",
            "schema_id": str(instance.schema_id),
            "value": {},
            "meta": {},
        }
