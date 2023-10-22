from typing import Any, Dict
import pytest
import pytest_asyncio
import dataclasses

from asgiref.sync import sync_to_async
from httpx import AsyncClient
from django.db.models import Model
from django.contrib.auth.models import AbstractUser, Group

from ix.server.fast_api import app
from ix.ix_users.tests.fake import afake_user


from fastapi import HTTPException


@dataclasses.dataclass
class OwnerState:
    owner: AbstractUser
    non_owner: AbstractUser
    object_owned: Model
    object_group_owned: Model
    object_global: Model


class OwnershipCreateTestsMixin:
    async def get_create_data(self) -> Dict[str, Any]:
        raise NotImplementedError

    async def test_unauthenticated_create(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that an unauthenticated user cannot create an object.
        Expected outcome: The server should return a 401 status code.
        """
        arequest_user.side_effect = HTTPException(
            status_code=401, detail="Not authenticated"
        )
        data = await self.get_create_data()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f"/{self.object_type}/", json=data)
            assert response.status_code == 401


class OwnershipListTestsMixin:
    async def test_owned_list(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user can list objects they own.
        Expected outcome: The server should return a 200 status code.
        """
        arequest_user.return_value = owner_state.owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/{self.object_type}/?limit=10000")
            assert response.status_code == 200

        # response should contain owned and global objects
        # check ids individually since there may be objects from other tests
        data = response.json()
        ids = {str(obj["id"]) for obj in data["objects"]}
        assert str(owner_state.object_owned.id) in ids
        assert str(owner_state.object_global.id) in ids

    async def test_not_owned_list(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user cannot list objects they do not own.
        Expected outcome: The server should return a 404 status code.
        """
        arequest_user.return_value = owner_state.non_owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/{self.object_type}/?limit=10000")
            assert response.status_code == 200

        # response should only contain global objects
        data = response.json()
        assert len(data["objects"]) >= 1
        ids = {str(obj["id"]) for obj in data["objects"]}
        assert str(owner_state.object_global.id) in ids
        assert str(owner_state.object_owned.id) not in ids

    async def test_group_owned_list(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user can list objects their group owns.
        Expected outcome: The server should return a 200 status code.
        """
        arequest_user.return_value = owner_state.owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/{self.object_type}/?limit=10000")
            assert response.status_code == 200

        # response should contain group owned and global objects
        data = response.json()
        ids = {str(obj["id"]) for obj in data["objects"]}
        assert str(owner_state.object_group_owned.id) in ids

    async def test_group_not_owned_list(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user cannot list objects not owned by their group.
        Expected outcome: The server should return a 403 status code.
        """
        arequest_user.return_value = owner_state.non_owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/{self.object_type}/?limit=10000")
            assert response.status_code == 200

            # response should only contain global objects
            data = response.json()
            assert len(data["objects"]) >= 1
            ids = {str(obj["id"]) for obj in data["objects"]}
            assert str(owner_state.object_global.id) in ids
            assert str(owner_state.object_owned.id) not in ids

    async def test_unauthenticated_list(self, arequest_user):
        """
        Test to verify that an unauthenticated user cannot get a list of objects.
        Expected outcome: The server should return a 401 status code.
        """
        arequest_user.side_effect = HTTPException(
            status_code=401, detail="Not authenticated"
        )
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/{self.object_type}/")
            assert response.status_code == 401


class OwnershipRetrieveTestsMixin:
    async def test_owned_detail(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user can access an object they own.
        Expected outcome: The server should return a 200 status code.
        """
        arequest_user.return_value = owner_state.owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/{self.object_type}/{owner_state.object_owned.id}"
            )
            assert response.status_code == 200

    async def test_group_owned_detail(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user can access an object their group owns.
        Expected outcome: The server should return a 200 status code.
        """
        arequest_user.return_value = owner_state.owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/{self.object_type}/{owner_state.object_group_owned.id}"
            )
            assert response.status_code == 200

    async def test_not_owned_detail(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user cannot access an object they do not own.
        Expected outcome: The server should return a 404 status code.
        """
        arequest_user.return_value = owner_state.non_owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/{self.object_type}/{owner_state.object_owned.id}"
            )
            assert (
                response.status_code == 404
            )  # Assuming the user cannot access not owned objects

    async def test_group_not_owned_detail(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user cannot access an object not owned by their group.
        Expected outcome: The server should return a 403 status code.
        """
        arequest_user.return_value = owner_state.non_owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/{self.object_type}/{owner_state.object_group_owned.id}"
            )
            assert response.status_code == 404

    async def test_unauthenticated_detail(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that an unauthenticated user cannot access an object.
        Expected outcome: The server should return a 401 status code.
        """
        arequest_user.side_effect = HTTPException(
            status_code=401, detail="Not authenticated"
        )

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/{self.object_type}/{owner_state.object_owned.id}"
            )
            assert response.status_code == 401


class OwnershipUpdateTestsMixin:
    async def get_update_data(self, instance: Model) -> Dict[str, Any]:
        raise NotImplementedError

    async def test_owned_update(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user can update an object they own.
        Expected outcome: The server should return a 200 status code.
        """
        arequest_user.return_value = owner_state.owner
        data = await self.get_update_data(owner_state.object_owned)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/{self.object_type}/{owner_state.object_owned.id}", json=data
            )
            assert response.status_code == 200, response.text

    async def test_group_owned_update(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user can update an object their group owns.
        Expected outcome: The server should return a 200 status code.
        """
        arequest_user.return_value = owner_state.owner
        data = await self.get_update_data(owner_state.object_group_owned)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/{self.object_type}/{owner_state.object_group_owned.id}", json=data
            )
            assert response.status_code == 200, response.text

    async def test_not_owned_update(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user cannot update an object they do not own.
        Expected outcome: The server should return a 404 status code.
        """
        arequest_user.return_value = owner_state.non_owner
        data = await self.get_update_data(owner_state.object_owned)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/{self.object_type}/{owner_state.object_owned.id}", json=data
            )
            assert response.status_code == 404, response.text

    async def test_group_not_owned_update(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user cannot update an object not owned by their group.
        Expected outcome: The server should return a 403 status code.
        """
        arequest_user.return_value = owner_state.non_owner
        data = await self.get_update_data(owner_state.object_group_owned)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/{self.object_type}/{owner_state.object_group_owned.id}", json=data
            )
            assert response.status_code == 404

    async def test_unauthenticated_update(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that an unauthenticated user cannot update an object.
        Expected outcome: The server should return a 401 status code.
        """
        arequest_user.side_effect = HTTPException(
            status_code=401, detail="Not authenticated"
        )
        data = await self.get_update_data(owner_state.object_owned)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/{self.object_type}/{owner_state.object_owned.id}", json=data
            )
            assert response.status_code == 401, response.text


class OwnershipUpdateGlobalsRestrictedTestsMixin:
    """Tests for when globals are restricted to admins"""

    async def test_update_global_admin(self, owner_state: OwnerState, arequest_admin):
        data = await self.get_update_data(owner_state.object_global)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/{self.object_type}/{owner_state.object_global.id}", json=data
            )
            assert response.status_code == 200

    async def test_update_global_not_admin(
        self, owner_state: OwnerState, arequest_user
    ):
        data = await self.get_update_data(owner_state.object_global)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/{self.object_type}/{owner_state.object_global.id}", json=data
            )
            assert response.status_code == 404


class OwnershipDeleteTestsMixin:
    async def test_owned_delete(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user can delete an object they own.
        Expected outcome: The server should return a 200 status code.
        """
        arequest_user.return_value = owner_state.owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(
                f"/{self.object_type}/{owner_state.object_owned.id}"
            )
            assert response.status_code == 200

    async def test_group_owned_delete(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user can delete an object their group owns.
        Expected outcome: The server should return a 200 status code.
        """
        arequest_user.return_value = owner_state.owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(
                f"/{self.object_type}/{owner_state.object_group_owned.id}"
            )
            assert response.status_code == 200

    async def test_not_owned_delete(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user cannot delete an object they do not own.
        Expected outcome: The server should return a 404 status code.
        """
        arequest_user.return_value = owner_state.non_owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(
                f"/{self.object_type}/{owner_state.object_owned.id}"
            )
            assert response.status_code == 404

    async def test_group_not_owned_delete(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user cannot delete an object not owned by their group.
        Expected outcome: The server should return a 403 status code.
        """
        arequest_user.return_value = owner_state.non_owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(
                f"/{self.object_type}/{owner_state.object_group_owned.id}"
            )
            assert response.status_code == 404

    async def test_unauthenticated_delete(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that an unauthenticated user cannot delete an object.
        Expected outcome: The server should return a 401 status code.
        """
        arequest_user.side_effect = HTTPException(
            status_code=401, detail="Not authenticated"
        )

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(
                f"/{self.object_type}/{owner_state.object_owned.id}"
            )
            assert response.status_code == 401


class OwnershipDeleteGlobalsRestrictedTestsMixin:
    """Tests for when globals are restricted to admins"""

    async def test_delete_global_admin(self, owner_state: OwnerState, arequest_admin):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(
                f"/{self.object_type}/{owner_state.object_global.id}"
            )
            assert response.status_code == 200

    async def test_delete_global_not_admin(
        self, owner_state: OwnerState, arequest_user
    ):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(
                f"/{self.object_type}/{owner_state.object_global.id}"
            )
            assert response.status_code == 404


class OwnershipTestsBaseMixin:
    """
    Mixin for testing access to API endpoints based on ownership.

    Attributes:
    - object_type (str): The type of object under test (e.g., 'agents').
    - setup_object (callable): A method to create the object instance for testing.

    Example:
    ```
    class TestAgent(OwnershipTestsMixin):
        object_type = "agents"

        async def setup_object(self, **kwargs):
            return await afake_agent(**kwargs)

        async def get_create_data(self) -> Dict[str, Any]:
            return {}

        async def get_update_data(self, instance: Model) -> Dict[str, Any]:
            return {}
    ```
    """

    object_type: str  # e.g., 'agents'
    setup_object: callable  # A method to setup the object

    async def setup_object(self, **kwargs):
        raise NotImplementedError

    @pytest.fixture(autouse=True)
    def owner_filtering(self, settings):
        settings.OWNER_FILTERING = True
        yield

    @pytest_asyncio.fixture
    async def owner_state(self, settings) -> OwnerState:
        owner_user = await afake_user(username="owner")
        non_owner_user = await afake_user(username="non-owner")
        group, _ = await Group.objects.aget_or_create(name="Test Group")
        await sync_to_async(owner_user.groups.add)(group.id)
        object_owned = await self.setup_object(user=owner_user)
        object_group_owned = await self.setup_object(user=None, group=group)
        object_global = await self.setup_object(user=None, group=None)

        # sanity check that setup_object is working for the specific test
        assert object_owned.user_id == owner_user.id
        assert object_owned.group_id is None
        assert object_group_owned.user_id is None
        assert object_group_owned.group_id == group.id
        assert object_global.user_id is None
        assert object_global.group_id is None

        return OwnerState(
            owner=owner_user,
            non_owner=non_owner_user,
            object_owned=object_owned,
            object_group_owned=object_group_owned,
            object_global=object_global,
        )

    async def test_owned_global(self, owner_state: OwnerState, arequest_user):
        """
        Test to verify that a logged-in user can access a global object.
        Expected outcome: The server should return a 200 status code.
        """
        arequest_user.return_value = owner_state.owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/{self.object_type}/{owner_state.object_global.id}"
            )
            assert (
                response.status_code == 200
            )  # Assuming the user can access global objects


class OwnershipTestsMixin(
    OwnershipTestsBaseMixin,
    OwnershipCreateTestsMixin,
    OwnershipUpdateTestsMixin,
    OwnershipDeleteTestsMixin,
    OwnershipListTestsMixin,
    OwnershipRetrieveTestsMixin,
):
    pass
