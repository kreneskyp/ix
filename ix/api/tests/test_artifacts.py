import tempfile

from fastapi.exceptions import HTTPException
import pytest_asyncio
from ix.server.fast_api import app
import pytest
from uuid import uuid4
from httpx import AsyncClient

from ix.task_log.models import Artifact, Task
from ix.task_log.tests.fake import afake_task, afake_artifact, afake_chat
from ix.ix_users.tests.mixins import (
    OwnerState,
    OwnershipTestsBaseMixin,
    OwnershipCreateTestsMixin,
    OwnershipUpdateTestsMixin,
    OwnershipListTestsMixin,
    OwnershipRetrieveTestsMixin,
)


@pytest_asyncio.fixture
async def mock_file():
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"test content")
        f.seek(0)
        yield f


@pytest.mark.django_db
class TestArtifact:
    async def test_create_artifact(self, anode_types):
        task = await afake_task()
        data = {
            "task_id": str(task.id),
            "key": "artifact_key",
            "artifact_type": "file",
            "name": "New Artifact",
            "description": "Artifact description",
            "storage": {"file": "/this/is/a/mock/path"},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/artifacts/", json=data)

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["name"] == "New Artifact"
        assert result["key"] == "artifact_key"
        assert result["task_id"] == str(task.id)
        assert result["artifact_type"] == "file"
        assert result["description"] == "Artifact description"
        assert result["storage"] == {"file": "/this/is/a/mock/path"}

    async def test_get_artifact(self, anode_types):
        task = await afake_task()
        artifact = await afake_artifact(task=task)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/artifacts/{artifact.id}")

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["id"] == str(artifact.id)
        assert result["name"] == artifact.name
        assert result["key"] == artifact.key
        assert result["task_id"] == str(artifact.task_id)
        assert result["artifact_type"] == artifact.artifact_type
        assert result["description"] == artifact.description
        assert result["storage"] == artifact.storage

    async def test_get_artifacts(self, anode_types):
        await Artifact.objects.all().adelete()
        task = await afake_task()
        artifact_1 = await afake_artifact(name="Artifact 1", key="key_1", task=task)
        artifact_2 = await afake_artifact(name="Artifact 2", key="key_2", task=task)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/artifacts/")

        assert response.status_code == 200, response.content
        page = response.json()
        objects = page["objects"]
        assert len(objects) == 2
        artifact_ids = [artifact["id"] for artifact in objects]
        assert str(artifact_1.id) in artifact_ids
        assert str(artifact_2.id) in artifact_ids

    async def test_get_artifacts_for_chat(self, anode_types):
        chat = await afake_chat()
        await Artifact.objects.all().adelete()
        task = await Task.objects.aget(pk=chat.task_id)
        task2 = await afake_task()
        artifact_1 = await afake_artifact(name="Artifact 1", key="key_1", task=task)
        artifact_2 = await afake_artifact(name="Artifact 2", key="key_2", task=task2)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/artifacts/", params={"chat_id": str(chat.id)})

        assert response.status_code == 200, response.content
        page = response.json()
        objects = page["objects"]
        assert len(objects) == 1
        artifact_ids = [artifact["id"] for artifact in objects]
        assert str(artifact_1.id) in artifact_ids
        assert str(artifact_2.id) not in artifact_ids

    async def test_update_artifact(self, anode_types):
        task = await afake_task()
        artifact = await afake_artifact(task=task)

        data = {
            "task_id": str(artifact.task_id),
            "name": "Updated Artifact",
            "key": "updated_key",
            "artifact_type": "file",
            "description": "Artifact description",
            "storage": {"file": "/this/is/a/mock/path"},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/artifacts/{artifact.id}", json=data)

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["name"] == "Updated Artifact"
        assert result["key"] == "updated_key"

    async def test_update_agent_not_found(self, anode_types):
        task = await afake_task()
        non_existent_id = uuid4()

        data = {
            "task_id": str(task.id),
            "name": "Updated Artifact",
            "key": "updated_key",
            "artifact_type": "file",
            "description": "Artifact description",
            "storage": {"file": "/this/is/a/mock/path"},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/artifacts/{non_existent_id}", json=data)

        assert response.status_code == 404, response.content
        result = response.json()
        assert result["detail"] == "Artifact not found"

    async def test_artifact_not_found(self):
        non_existent_artifact_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/artifacts/{non_existent_artifact_id}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Artifact not found"

    async def test_download_artifact(self, mock_file, anode_types):
        task = await afake_task()
        artifact = await afake_artifact(task_id=task.id, storage={"id": mock_file.name})
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/artifacts/{artifact.id}/download")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/octet-stream"
        assert (
            response.headers["content-disposition"]
            == f'attachment; filename="{artifact.storage["id"].split("/")[-1]}"'
        )
        assert response.content == b"test content"


@pytest.mark.django_db
@pytest.mark.usefixtures("anode_types")
class TestArtifactOwnership(
    OwnershipTestsBaseMixin,
    OwnershipCreateTestsMixin,
    OwnershipUpdateTestsMixin,
    OwnershipListTestsMixin,
    OwnershipRetrieveTestsMixin,
):
    object_type = "artifacts"

    async def setup_object(self, **kwargs):
        task = await afake_task()
        return await afake_artifact(task_id=task.id, **kwargs)

    async def get_create_data(self):
        task = await afake_task()
        return {
            "task_id": str(task.id),
            "name": "New Artifact",
            "key": "new_key",
            "artifact_type": "file",
            "description": "Artifact description",
            "storage": {"file": "/this/is/a/mock/path"},
        }

    async def get_update_data(self, instance):
        return {
            "task_id": str(instance.task_id),
            "name": "Updated Artifact",
            "key": "updated_key",
            "artifact_type": "file",
            "description": "Artifact description",
            "storage": {"file": "/this/is/a/mock/path"},
        }

    async def test_download_artifact_ownership_user_owns(
        self, mock_file, owner_state: OwnerState, arequest_user
    ):
        arequest_user.return_value = owner_state.owner
        owner_state.object_owned.storage["id"] = mock_file.name
        await owner_state.object_owned.asave()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/artifacts/{owner_state.object_owned.id}/download",
            )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/octet-stream"
        assert (
            response.headers["content-disposition"]
            == f'attachment; filename="{owner_state.object_owned.storage["id"].split("/")[-1]}"'
        )
        assert response.content == b"test content"

    async def test_download_artifact_ownership_user_does_not_own(
        self, mock_file, owner_state: OwnerState, arequest_user
    ):
        arequest_user.return_value = owner_state.non_owner

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/artifacts/{owner_state.object_owned.id}/download",
            )
        assert response.status_code == 404

    async def test_download_artifact_ownership_group_owns(
        self, mock_file, owner_state: OwnerState, arequest_user
    ):
        arequest_user.return_value = owner_state.owner
        owner_state.object_group_owned.storage["id"] = mock_file.name
        await owner_state.object_group_owned.asave()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/artifacts/{owner_state.object_group_owned.id}/download",
            )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/octet-stream"
        assert (
            response.headers["content-disposition"]
            == f'attachment; filename="{owner_state.object_group_owned.storage["id"].split("/")[-1]}"'
        )
        assert response.content == b"test content"

    async def test_download_artifact_ownership_group_does_not_own(
        self, mock_file, owner_state: OwnerState, arequest_user
    ):
        arequest_user.return_value = owner_state.non_owner
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/artifacts/{owner_state.object_group_owned.id}/download",
            )
        assert response.status_code == 404

    async def test_download_artifact_ownership_unauthenticated(
        self, mock_file, owner_state: OwnerState, arequest_user
    ):
        arequest_user.side_effect = HTTPException(
            status_code=401, detail="Not authenticated"
        )

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(
                f"/artifacts/{owner_state.object_owned.id}/download"
            )
        assert response.status_code == 401
