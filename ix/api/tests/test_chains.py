from uuid import uuid4

import pytest
from httpx import AsyncClient

from ix.server.fast_api import app
from ix.chains.models import ChainEdge, ChainNode, Chain, NodeType
from ix.chains.tests.mock_chain import MOCK_CHAIN_CONFIG
from ix.task_log.tests.fake import (
    afake_chain_node,
    afake_chain_edge,
    afake_chain,
)


@pytest.mark.django_db
class TestChain:
    async def test_create_chain(self, anode_types):
        chain_data = {
            "name": "New Chain",
            "description": "A new chain",
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/chains/", json=chain_data)

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["chain"]["name"] == "New Chain"

    async def test_create_chain_with_id(self, anode_types):
        chain_data = {
            "id": str(uuid4()),
            "name": "New Chain",
            "description": "A new chain",
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/chains/", json=chain_data)

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["chain"]["id"] == str(chain_data["id"])

    async def test_update_chain(self, anode_types):
        # Create a chain to update
        chain = await afake_chain()
        update_data = {
            "name": "Updated Chain",
            "description": "Updated Chain",
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/chains/{chain.id}", json=update_data)

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["chain"]["name"] == "Updated Chain"

    async def test_delete_chain(self, anode_types):
        # Create a chain to delete
        chain = await afake_chain()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/chains/{chain.id}")

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["chain_id"] == str(chain.id)
        assert await Chain.objects.filter(id=chain.id).acount() == 0

    async def test_update_non_existent_chain(self):
        # Prepare data for a non-existent chain
        non_existent_chain_id = uuid4()
        update_data = {
            "name": "Updated Chain",
            "description": "Updated Chain",
            "config": {},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/chains/{non_existent_chain_id}", json=update_data
            )

        assert response.status_code == 404, response.content
        result = response.json()
        assert result["detail"] == "Chain not found"

    async def test_delete_non_existent_chain(self):
        # Prepare a non-existent chain id
        non_existent_chain_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/chains/{non_existent_chain_id}")

        assert response.status_code == 404, response.content
        result = response.json()
        assert result["detail"] == "Chain not found"


@pytest.mark.django_db
class TestNode:
    async def test_add_first_node(self, anode_types):
        """
        The first node will create the chain
        """
        chain = await afake_chain()
        data = {
            "class_path": "ix.chains.llm_chain.LLMChain",
            "config": {},
            "name": "Custom Node",
            "chain_id": str(chain.id),
            "description": "Custom Description",
            "position": {
                "x": 10,
                "y": 20,
            },
        }

        # Execute the API request
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/chain/nodes", json=data)

        # Assert the result
        assert response.status_code == 200, response.json()
        node_data = response.json()
        assert node_data["id"] is not None
        assert node_data["name"] == "Custom Node"
        assert node_data["description"] == "Custom Description"
        assert node_data["position"] == {
            "x": 10,
            "y": 20,
        }

        # assert models
        node = await ChainNode.objects.aget(id=node_data["id"])
        assert node.chain_id is not None

    async def test_update_node(self, anode_types):
        # Create a chain node to update
        node = await afake_chain_node()

        # Prepare data for the API request
        data = {
            "name": "Updated Node",
            "description": "Updated Description",
            "position": {
                "x": 10,
                "y": 20,
            },
            "config": {"foo": "bar"},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/chain/nodes/{node.id}", json=data)

        # Assert the result
        assert response.status_code == 200, response.json()
        node_data = response.json()
        assert node_data["id"] == str(node.id)
        assert node_data["name"] == "Updated Node"
        assert node_data["description"] == "Updated Description"
        assert node_data["position"] == {
            "x": 10,
            "y": 20,
        }

    async def test_delete_node(self, anode_types):
        # Create a chain node to delete
        node = await afake_chain_node(config=MOCK_CHAIN_CONFIG)
        source_node = await afake_chain_node(chain=node.chain, config=MOCK_CHAIN_CONFIG)
        target_node = await afake_chain_node(chain=node.chain, config=MOCK_CHAIN_CONFIG)
        edge_in = await afake_chain_edge(source=source_node, target=node)
        edge_out = await afake_chain_edge(source=node, target=target_node)

        # Execute the API request
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/chain/nodes/{node.id}")

        # Assert the result
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["node_id"] == str(node.id)
        assert await ChainNode.objects.filter(id=node.id).acount() == 0
        assert await ChainEdge.objects.filter(id=edge_in.id).acount() == 0
        assert await ChainEdge.objects.filter(id=edge_out.id).acount() == 0


@pytest.mark.django_db
class TestNodePosition:
    async def test_update_position(self, anode_types):
        """
        Update just the position of a node
        """
        assert not await Chain.objects.filter(name="Custom Node").aexists()

        node = await afake_chain_node()

        # Prepare data for the API request
        data = {
            "x": 100,
            "y": 200,
        }

        # Execute the API request
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f"/chain/nodes/{node.id}/position", json=data)

        # Assert the result
        assert response.status_code == 200, response.json()
        node_data = response.json()["node"]
        assert node_data["id"] is not None
        assert node_data["position"] == {
            "x": 100,
            "y": 200,
        }


@pytest.mark.django_db
class TestChainEdge:
    async def test_add_chain_edge(self, anode_types):
        # Create a chain and nodes
        chain = await afake_chain()
        node1 = await afake_chain_node(chain=chain)
        node2 = await afake_chain_node(chain=chain)
        edge_id = str(uuid4())

        # Prepare data for the API request
        data = {
            "id": edge_id,
            "source_id": str(node1.id),
            "target_id": str(node2.id),
            "key": "Custom Key",
            "chain_id": str(chain.id),
            "relation": "LINK",
            "input_map": {},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/chain/edges", json=data)

        # Assert the result
        assert response.status_code == 200, response.json()
        edge_data = response.json()["edge"]
        assert edge_data["id"] == edge_id
        assert edge_data["source_id"] == str(node1.id)
        assert edge_data["target_id"] == str(node2.id)
        assert edge_data["key"] == "Custom Key"
        assert edge_data["input_map"] == {}

    async def test_update_chain_edge(self, anode_types):
        # Create a chain edge to update
        edge = await afake_chain_edge()

        chain = await afake_chain()
        node1 = await afake_chain_node(chain=chain, config={})
        node2 = await afake_chain_node(chain=chain, config={})

        # Prepare data for the API request
        data = {
            "source_id": str(node1.id),
            "target_id": str(node2.id),
            "key": "Updated Key",
            "relation": "LINK",
            "input_map": {"param1": "value1", "param2": "value2"},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/chain/edges/{edge.id}", json=data)

        # Assert the result
        assert response.status_code == 200, response.json()
        edge_data = response.json()["edge"]
        assert edge_data["id"] == str(edge.id)
        assert edge_data["key"] == "Updated Key"
        assert edge_data["input_map"] == {"param1": "value1", "param2": "value2"}

    async def test_delete_chain_edge(self, anode_types):
        # Create a chain edge to delete
        edge = await afake_chain_edge()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/chain/edges/{edge.id}")

        # Assert the result
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["edge_id"] == str(edge.id)
        assert await ChainEdge.objects.filter(id=edge.id).acount() == 0


@pytest.mark.django_db
class TestChainGraph:
    async def test_add_chain_edge(self, anode_types):
        chain = await afake_chain()
        node1 = await afake_chain_node(chain=chain)
        node2 = await afake_chain_node(chain=chain)
        await afake_chain_edge(source=node1, target=node2)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/chain/{chain.id}/graph")

        assert response.status_code == 200, response.content
        data = response.json()
        assert data["chain"]["id"] == str(chain.id)
        node_ids = {node["id"] for node in data["nodes"]}
        assert node_ids == {str(node.id) for node in await chain.nodes.all()}
        edge_ids = {edge["id"] for edge in data["edges"]}
        assert edge_ids == {str(edge.id) for edge in await chain.edges.all()}
