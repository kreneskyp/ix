from ix.server.fast_api import app
import pytest
from uuid import uuid4
from httpx import AsyncClient

from ix.task_log.models import Artifact, Task
from ix.task_log.tests.fake import afake_task, afake_artifact, afake_chat


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
