from ix.ix_users.tests.mixins import OwnershipTestsMixin
from ix.server.fast_api import app
import pytest
from ix.agents.models import Agent
from uuid import uuid4
from httpx import AsyncClient

from ix.task_log.tests.fake import afake_agent, afake_chain


@pytest.mark.django_db
class TestAgent:
    async def test_get_agents(self, auser, anode_types):
        agent_1 = await afake_agent(name="Mock Agent 1", alias="mock_agent_1")
        agent_2 = await afake_agent(name="Mock Agent 2", alias="mock_agent_2")
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/agents/")

        assert response.status_code == 200, response.content
        page = response.json()

        # Check that we got a list of agents
        objects = page["objects"]
        assert len(objects) >= 2
        agent_ids = [agent["id"] for agent in objects]
        assert str(agent_1.id) in agent_ids
        assert str(agent_2.id) in agent_ids

    async def test_search_agents(self, achat):
        search_term = "mock"

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/agents/?search={search_term}")

        assert response.status_code == 200, response.content
        page = response.json()
        objects = page["objects"]
        assert len(objects) > 0
        assert (
            search_term in objects[0]["name"]
            or search_term in objects[0]["purpose"]
            or search_term in objects[0]["alias"]
        )

    async def test_get_agent_detail(self, anode_types):
        agent = await afake_agent()
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/agents/{agent.id}")

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we got the correct agent detail
        assert result["id"] == str(agent.id)
        assert result["name"] == agent.name
        assert result["chain_id"] == str(agent.chain_id)
        assert result["alias"] == agent.alias
        assert result["purpose"] == agent.purpose
        assert result["model"] == agent.model

    async def test_get_agent_detail_not_found(self, anode_types):
        non_existent_agent_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/agents/{non_existent_agent_id}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Agent not found"

    async def test_create_agent(self):
        chain = await afake_chain()
        data = {
            "name": "New Agent",
            "alias": "new_guy",
            "purpose": "New Agent Purpose",
            "model": "gpt-4",
            "chain_id": str(chain.id),
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/agents/", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we created the agent
        assert result["name"] == "New Agent"
        assert result["chain_id"] == str(chain.id)
        assert result["alias"] == "new_guy"
        assert result["purpose"] == "New Agent Purpose"
        assert result["model"] == "gpt-4"

    async def test_update_agent(self):
        agent = await afake_agent()
        chain = await afake_chain()
        data = {
            "name": "New Agent",
            "alias": "new_guy",
            "purpose": "New Agent Purpose",
            "model": "gpt-4",
            "chain_id": str(chain.id),
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/agents/{agent.id}", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we updated the agent
        # Check that we created the agent
        assert result["name"] == "New Agent"
        assert result["chain_id"] == str(chain.id)
        assert result["alias"] == "new_guy"
        assert result["purpose"] == "New Agent Purpose"
        assert result["model"] == "gpt-4"

    async def test_update_agent_not_found(self):
        agent = await afake_agent()
        non_existent_agent_id = uuid4()

        # Prepare the data for the API request
        data = {
            "name": "New Agent",
            "alias": "new_guy",
            "purpose": "New Agent Purpose",
            "model": "gpt-4",
            "chain_id": str(agent.chain_id),
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/agents/{non_existent_agent_id}", json=data)

        assert response.status_code == 404, response.content
        result = response.json()
        assert result["detail"] == "Agent not found"

    async def test_delete_agent(self, anode_types):
        agent = await afake_agent()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/agents/{agent.id}")

        # Assert the result
        assert response.status_code == 200, response.content
        result = response.json()
        assert result["id"] == str(agent.id)

        # Ensure the agent is deleted
        assert not await Agent.objects.filter(id=agent.id).aexists()

    async def test_delete_agent_not_found(self, node_types):
        non_existent_agent_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/agents/{non_existent_agent_id}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Agent not found"


@pytest.mark.django_db
@pytest.mark.usefixtures("anode_types")
class TestAgentOwnership(OwnershipTestsMixin):
    object_type = "agents"

    async def setup_object(self, **kwargs):
        return await afake_agent(**kwargs)

    async def get_create_data(self):
        chain = await afake_chain()
        return {
            "name": "New Agent",
            "alias": "new_guy",
            "purpose": "New Agent Purpose",
            "model": "gpt-4",
            "chain_id": str(chain.id),
        }

    async def get_update_data(self, instance):
        return {
            "name": "New Agent",
            "alias": "new_guy",
            "purpose": "New Agent Purpose",
            "model": "gpt-4",
            "chain_id": str(instance.chain_id),
        }
