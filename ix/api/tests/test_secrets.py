import pytest_asyncio
from pydantic import BaseModel

from ix.ix_users.tests.mixins import OwnershipTestsMixin
from ix.secrets.vault import UserVaultClient
from ix.server.fast_api import app
import pytest
from ix.secrets.models import Secret, SecretType
from uuid import uuid4
from httpx import AsyncClient

from ix.secrets.tests.fake import (
    MockAccount,
    afake_secret,
    afake_secret_type,
    aget_mock_secret_type,
)
from ix.ix_users.tests.fake import afake_group, afake_user


@pytest_asyncio.fixture
async def asecret_type() -> SecretType:
    return await aget_mock_secret_type()


@pytest.mark.django_db
class TestSecretTypes:
    async def test_create_secret_type(self, auser):
        data = {"name": "Test Secret Type", "fields_schema": MockAccount.schema()}

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/secret_types/", json=data)

        assert response.status_code == 200, response.content

        result = response.json()
        assert result["name"] == "Test Secret Type"
        assert result["user_id"] == auser.id
        assert result["group_id"] is None
        assert result["fields_schema"] == MockAccount.schema()

        secret_type = await SecretType.objects.aget(id=result["id"])
        assert secret_type.name == "Test Secret Type"
        assert secret_type.user_id == auser.id
        assert secret_type.fields_schema == MockAccount.schema()
        assert secret_type.group_id is None

    async def test_get_secret_types(self, auser):
        secret_type_1 = await afake_secret_type(name="Secret Type 1")
        secret_type_2 = await afake_secret_type(name="Secret Type 2")

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/secret_types/")

        assert response.status_code == 200, response.content
        page = response.json()

        # Check that we got a list of secret types
        objects = page["objects"]
        assert len(objects) >= 2
        object_ids = [secret_type["id"] for secret_type in objects]
        assert str(secret_type_1.id) in object_ids
        assert str(secret_type_2.id) in object_ids

    async def test_update_secret_type(self, auser):
        secret_type = await afake_secret_type(name="Old Secret Type")

        class NewAccount(BaseModel):
            different_key: str

        data = {"name": "New Secret Type", "fields_schema": NewAccount.schema()}

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/secret_types/{secret_type.id}", json=data)

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["name"] == "New Secret Type"
        assert result["user_id"] == auser.id
        assert result["group_id"] is None
        assert result["fields_schema"] == NewAccount.schema()

        updated_secret_type = await SecretType.objects.aget(id=result["id"])
        assert updated_secret_type.name == "New Secret Type"
        assert updated_secret_type.user_id == auser.id
        assert updated_secret_type.group_id is None
        assert updated_secret_type.fields_schema == NewAccount.schema()

    async def test_cant_change_user_or_group(self, auser):
        new_user = await afake_user()
        new_group = await afake_group()

        secret_type = await afake_secret_type(name="Secret Type")

        data = {
            "name": "Updated Secret Type",
            "fields_schema": MockAccount.schema(),
            "user_id": new_user.id,
            "group_id": new_group.id,
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/secret_types/{secret_type.id}", json=data)
        assert response.status_code == 200, response.content

        await secret_type.arefresh_from_db()
        assert not secret_type.user_id == new_user.id
        assert not secret_type.group_id == new_group.id

    async def test_delete_secret_type(self, auser):
        secret_type = await afake_secret_type(name="Secret Type to Delete")

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/secret_types/{secret_type.id}")

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["id"] == str(secret_type.id)
        assert not await SecretType.objects.filter(id=secret_type.id).aexists()


@pytest.mark.django_db
@pytest.mark.usefixtures("clean_vault")
class TestSecrets:
    async def test_get_secrets(self, auser, asecret_type):
        secret_1 = await afake_secret(path="Mock Secret 1")
        secret_2 = await afake_secret(path="Mock Secret 2")

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/secrets/")

        assert response.status_code == 200, response.content
        page = response.json()

        # Check that we got a list of agents
        objects = page["objects"]
        assert len(objects) >= 2
        object_ids = [agent["id"] for agent in objects]
        assert str(secret_1.id) in object_ids
        assert str(secret_2.id) in object_ids
        object_1 = objects[0]
        assert object_1["path"] == f"{asecret_type.id}/{secret_1.pk}"
        assert object_1["name"] == "default instance"
        assert object_1["user_id"] == auser.id
        assert object_1["type_id"] == str(asecret_type.id)

    async def test_create_secret(self, auser, asecret_type):
        data = {
            "type_id": str(asecret_type.id),
            "name": "default key",
            "value": {"test": "value"},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/secrets/", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        secret = await Secret.objects.aget(id=result["id"])
        assert result["path"] == f"{asecret_type.id}/{secret.pk}"
        assert result["name"] == "default key"
        assert result["user_id"] == auser.id
        assert result["type_id"] == str(asecret_type.id)

    async def test_create_unauthorized_secret(self, auser, asecret_type):
        """Test creating a secret for someone else's user_id
        user_id is ignored and secret is created for themselves.
        """
        user2 = await afake_user()
        data = {
            "user_id": user2.id,
            "type_id": str(asecret_type.id),
            "name": "default key",
            "value": {"test": "value"},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/secrets/", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        secret = await Secret.objects.aget(id=result["id"])
        assert result["path"] == f"{asecret_type.id}/{secret.pk}"
        assert result["name"] == "default key"
        assert result["user_id"] == auser.id
        assert result["type_id"] == str(asecret_type.id)

    async def test_update_secret(self, auser, asecret_type):
        secret = await afake_secret()
        client = UserVaultClient(auser)
        client.write(secret.path, {"test": "value"})

        data = {
            "name": "Updated Secret",
            "type_id": str(asecret_type.id),
            "value": {"test": "updated value"},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/secrets/{secret.id}", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        assert result["name"] == "Updated Secret"
        assert "value" not in result

        # secret meta updated in db
        secret = await Secret.objects.aget(id=secret.id)
        assert secret.name == "Updated Secret"

        # secret value updated in vault
        assert client.read(secret.path) == {"test": "updated value"}

    async def test_delete_secret(self, auser):
        secret = await afake_secret(user=auser)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/secrets/{secret.id}")

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["id"] == str(secret.id)

        # Ensure the secret is deleted
        assert not await Secret.objects.filter(id=secret.id).aexists()

    async def test_delete_secret_not_found(self):
        non_existent_secret_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/secrets/{non_existent_secret_id}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Secret not found"

    async def test_get_secret_detail_not_found(self):
        non_existent_secret_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/secrets/{non_existent_secret_id}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Secret not found"


@pytest.mark.django_db
class TestSecretTypeOwnership(OwnershipTestsMixin):
    object_type = "secret_types"

    async def setup_object(self, **kwargs):
        return await afake_secret_type(**kwargs)

    async def get_create_data(self):
        return {
            "name": "Testing Service",
            "fields_schema": MockAccount.schema(),
        }

    async def get_update_data(self, instance):
        return {
            "name": "Testing Service",
            "fields_schema": MockAccount.schema(),
        }


@pytest.mark.django_db
@pytest.mark.usefixtures("clean_vault")
class TestSecretOwnership(OwnershipTestsMixin):
    object_type = "secrets"

    async def setup_object(self, **kwargs):
        secret_type = await aget_mock_secret_type()
        return await afake_secret(type_id=secret_type.id, **kwargs)

    async def get_create_data(self):
        secret_type = await aget_mock_secret_type()
        return {
            "name": "Test Account 1",
            "value": MockAccount(api_key="foo").model_dump(),
            "type_id": str(secret_type.id),
        }

    async def get_update_data(self, instance):
        return {
            "name": "Test Account 2",
            "value": MockAccount(api_key="bar").model_dump(),
            "type_id": str(instance.type_id),
        }
