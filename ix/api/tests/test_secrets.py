from ix.secrets.vault import UserVaultClient
from ix.server.fast_api import app
import pytest
from ix.secrets.models import Secret
from uuid import uuid4
from httpx import AsyncClient

from ix.secrets.tests.fake import afake_secret
from ix.ix_users.tests.fake import afake_user


@pytest.mark.django_db
class TestSecrets:
    async def test_get_secrets(self, auser):
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
        assert object_1["path"] == f"test_service/{secret_1.pk}"
        assert object_1["name"] == "default instance"
        assert object_1["user_id"] == auser.id
        assert object_1["type"] == "test_service"

    async def test_create_secret(self, auser):
        data = {
            "type": "test_service",
            "name": "default key",
            "value": {"test": "value"},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/secrets/", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        secret = await Secret.objects.aget(id=result["id"])
        assert result["path"] == f"test_service/{secret.pk}"
        assert result["name"] == "default key"
        assert result["user_id"] == auser.id
        assert result["type"] == "test_service"

    async def test_create_unauthorized_secret(self, auser):
        """Test creating a secret for someone else's user_id"""
        user2 = await afake_user()
        data = {
            "user_id": user2.id,
            "type": "test_service",
            "name": "default key",
            "value": {"test": "value"},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/secrets/", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        secret = await Secret.objects.aget(id=result["id"])
        assert result["path"] == f"test_service/{secret.pk}"
        assert result["name"] == "default key"
        assert result["user_id"] == auser.id
        assert result["type"] == "test_service"

    async def test_update_secret(self, auser):
        secret = await afake_secret()
        client = UserVaultClient(auser)
        client.write(secret.path, {"test": "value"})

        data = {
            "name": "Updated Secret",
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

    async def test_update_secret_unauthorized(self, auser):
        """Users shouldn't be able to update secrets that don't belong to them"""
        # sanity check clean environment
        await Secret.objects.all().adelete()
        assert await Secret.objects.acount() == 0

        await afake_user()
        user_2 = await afake_user()
        secret = await afake_secret(path="Sensitive Secret", user=user_2)

        data = {
            "name": "Updated Secret",
            "value": {"test": "updated value"},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/secrets/{secret.id}", json=data)

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Secret not found"

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

    async def test_delete_secret_unauthorized(self, auser):
        """Test that an unauthorized user can't delete secrets"""
        # sanity check clean environment
        await Secret.objects.all().adelete()
        assert await Secret.objects.acount() == 0

        await afake_user()
        user_2 = await afake_user()
        secret = await afake_secret(path="Sensitive Secret", user=user_2)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/secrets/{secret.id}")

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

    async def test_get_secrets_unauthorized(self):
        """Test that an unauthorized user can't access secrets"""
        # sanity check clean environment
        await Secret.objects.all().adelete()
        assert await Secret.objects.acount() == 0

        await afake_user()
        user_2 = await afake_user()
        await afake_secret(path="Sensitive Secret", user=user_2)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/secrets/")

        assert response.status_code == 200, response.content
        page = response.json()

        # Check that we got a empty list of agents
        objects = page["objects"]
        assert len(objects) == 0
