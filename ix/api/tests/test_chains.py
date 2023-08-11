from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient

from ix.server.fast_api import app
from ix.chains.models import ChainEdge, ChainNode, Chain, NodeType
from ix.chains.tests.mock_chain import MOCK_CHAIN_CONFIG
from ix.task_log.tests.fake import (
    afake_chain_node,
    afake_chain_edge,
    afake_chain,
)


@pytest_asyncio.fixture
async def amock_node_type(anode_types):
    return await NodeType.objects.aget(
        class_path="ix.chains.tests.mock_chain.MockChain"
    )


@pytest.mark.django_db
class TestNodeType:
    async def test_get_node_types(self, amock_node_type):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/node_types/")

        assert response.status_code == 200, response.content
        page = response.json()

        # Check that we got a list of node types
        objects = page["objects"]
        assert len(objects) >= 2

    async def test_search_node_types(self, anode_types):
        search_term = "mock"

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/node_types/?search={search_term}")

        assert response.status_code == 200, response.content
        page = response.json()
        objects = page["objects"]
        assert len(objects) > 0
        assert (
            search_term in objects[0]["name"]
            or search_term in objects[0]["description"]
            or search_term in objects[0]["type"]
            or search_term in objects[0]["class_path"]
        )

    async def test_get_node_type_detail(self, amock_node_type):
        # Create a node type
        node_type = amock_node_type
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/node_types/{node_type.id}")

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we got the correct node type detail
        assert result["id"] == str(node_type.id)
        assert result["name"] == "Mock Chain"

    async def test_get_node_type_detail_not_found(self):
        # Use a non-existent node_type_id
        non_existent_node_type_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/node_types/{non_existent_node_type_id}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Node type not found"

    async def test_create_node_type(self):
        node_type_data = {
            "name": "New Node Type",
            "description": "New Node Type Description",
            "class_path": "ix.chains.tests.DoesNotNeedToExistForTest",
            "type": "chain",
            "config": {},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/node_types/", json=node_type_data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we created the node type
        assert result["name"] == "New Node Type"

    async def test_update_node_type(self, amock_node_type):
        # Create a node type to update
        node_type = amock_node_type
        data = {
            "name": "Updated Node Type",
            "description": "Updated Node Type Description",
            "class_path": "ix.chains.tests.mock_chain.MockChainUpdated",
            "type": "llm",
            "config": {},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/node_types/{node_type.id}", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we updated the node type
        assert result["id"] == str(node_type.id)
        assert result["name"] == "Updated Node Type"
        assert result["type"] == "llm"
        assert result["class_path"] == "ix.chains.tests.mock_chain.MockChainUpdated"

    async def test_update_node_type_not_found(self):
        # Use a non-existent node_type_id
        non_existent_node_type_id = uuid4()

        # Prepare the data for the API request
        data = {
            "name": "Updated Node Type",
            "description": "Updated Node Type Description",
            "class_path": "ix.chains.tests.mock_chain.MockChainUpdated",
            "type": "llm",
            "config": {},
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/node_types/{non_existent_node_type_id}", json=data
            )

        assert response.status_code == 404, response.content
        result = response.json()
        assert result["detail"] == "Node type not found"

    async def test_delete_node_type(self, amock_node_type):
        # Create a node type to delete
        node_type = amock_node_type

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/node_types/{node_type.id}")

        # Assert the result
        assert response.status_code == 200, response.content
        result = response.json()
        assert result["id"] == str(node_type.id)

        # Ensure the node type is deleted
        assert not await NodeType.objects.filter(id=node_type.id).aexists()

    async def test_delete_node_type_not_found(self):
        # Use a non-existent node_type_id
        non_existent_node_type_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/node_types/{non_existent_node_type_id}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Node type not found"


@pytest.mark.django_db
class TestChain:
    async def test_get_chains(self, anode_types):
        # Clear existing chains
        await Chain.objects.all().adelete()

        # Create some chains
        chain1 = await afake_chain(name="Chain 1", description="Chain 1 Description")
        chain2 = await afake_chain(name="Chain 2", description="Chain 2 Description")

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/chains/")

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we got the correct chains back
        objects = result["objects"]
        assert len(objects) == 2
        chain_ids = {chain["id"] for chain in objects}
        assert str(chain1.id) in chain_ids
        assert str(chain2.id) in chain_ids

    async def test_get_chain_detail(self, anode_types):
        # Create a chain
        chain = await afake_chain(
            name="Test Chain", description="Test Chain Description"
        )

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/chains/{chain.id}")

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we got the correct chain detail
        assert result["id"] == str(chain.id)
        assert result["name"] == "Test Chain"
        assert result["description"] == "Test Chain Description"

    async def test_get_chain_detail_not_found(self):
        # Use a non-existent chain_id
        non_existent_chain_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/chains/{non_existent_chain_id}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Chain not found"

    async def test_create_chain(self, anode_types):
        chain_data = {
            "name": "New Chain",
            "description": "A new chain",
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/chains/", json=chain_data)

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["name"] == "New Chain"

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
        assert result["id"] == str(chain_data["id"])

    async def test_update_chain(self, anode_types):
        # Create a chain to update
        chain = await afake_chain()
        data = {
            "name": "Updated Chain",
            "description": "Updated Chain",
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/chains/{chain.id}", json=data)

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["name"] == "Updated Chain"

    async def test_delete_chain(self, anode_types):
        # Create a chain to delete
        chain = await afake_chain()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/chains/{chain.id}")

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["id"] == str(chain.id)
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
class TestChainRoot:
    async def test_set_chain_root_no_root_exists(self, anode_types):
        chain = await afake_chain()
        node = await afake_chain_node(chain=chain)
        await ChainNode.objects.filter(chain=chain).aupdate(root=False)
        data = {"node_id": str(node.id)}

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f"/chains/{chain.id}/set_root", json=data)

        assert response.status_code == 200
        result = response.json()
        assert result["root"] == str(node.id)
        assert result["old_roots"] == []
        await node.arefresh_from_db()
        assert node.root

    async def test_set_chain_root_exists(self, anode_types):
        chain = await afake_chain()
        old_root = await afake_chain_node(chain=chain, root=True)
        new_root = await afake_chain_node(chain=chain, root=False)

        data = {"node_id": str(new_root.id), "chain_id": str(chain.id)}
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f"/chains/{chain.id}/set_root", json=data)

        assert response.status_code == 200
        result = response.json()
        assert result["root"] == str(new_root.id)
        assert result["old_roots"] == [str(old_root.id)]
        await old_root.arefresh_from_db()
        await new_root.arefresh_from_db()
        assert new_root.root
        assert not old_root.root

    async def test_remove_chain_root(self, anode_types):
        chain = await afake_chain()
        root = await afake_chain_node(chain=chain, root=True)
        data = {"node_id": None, "chain_id": str(chain.id)}

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f"/chains/{chain.id}/set_root", json=data)

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["root"] is None
        assert result["old_roots"] == [str(root.id)]


@pytest.mark.django_db
class TestNode:
    async def test_add_first_node(self, anode_types):
        """
        The first node will create the chain
        """
        data = {
            "class_path": "ix.chains.llm_chain.LLMChain",
            "config": {},
            "name": "Custom Node",
            "description": "Custom Description",
            "position": {
                "x": 10,
                "y": 20,
            },
        }

        # Execute the API request
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/chains/nodes", json=data)

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
            response = await ac.put(f"/chains/nodes/{node.id}", json=data)

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

    async def test_update_non_existent_chain_node(self):
        non_existent_node_id = uuid4()
        update_data = {
            "name": "Updated Name",
            # add other fields to be updated...
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(
                f"/chains/nodes/{non_existent_node_id}", json=update_data
            )

        assert response.status_code == 404, response.content

    async def test_delete_node(self, anode_types):
        # Create a chain node to delete
        node = await afake_chain_node(config=MOCK_CHAIN_CONFIG)
        source_node = await afake_chain_node(chain=node.chain, config=MOCK_CHAIN_CONFIG)
        target_node = await afake_chain_node(chain=node.chain, config=MOCK_CHAIN_CONFIG)
        edge_in = await afake_chain_edge(source=source_node, target=node)
        edge_out = await afake_chain_edge(source=node, target=target_node)

        # Execute the API request
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/chains/nodes/{node.id}")

        # Assert the result
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == str(node.id)
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
            response = await ac.post(f"/chains/nodes/{node.id}/position", json=data)

        # Assert the result
        assert response.status_code == 200, response.json()
        node_data = response.json()
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
            response = await ac.post("/chains/edges", json=data)

        # Assert the result
        assert response.status_code == 200, response.json()
        edge_data = response.json()
        assert edge_data["id"] == edge_id
        assert edge_data["source_id"] == str(node1.id)
        assert edge_data["target_id"] == str(node2.id)
        assert edge_data["key"] == "Custom Key"
        assert edge_data["input_map"] == {}

    async def test_update_chain_edge(self, anode_types):
        # Create a chain edge to update
        edge = await afake_chain_edge()

        chain = await afake_chain()
        node1 = await afake_chain_node(chain=chain)
        node2 = await afake_chain_node(chain=chain)

        # Prepare data for the API request
        data = {
            "source_id": str(node1.id),
            "target_id": str(node2.id),
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/chains/edges/{edge.id}", json=data)

        # Assert the result
        assert response.status_code == 200, response.json()
        edge_data = response.json()
        assert edge_data["id"] == str(edge.id)

    async def test_delete_chain_edge(self, anode_types):
        # Create a chain edge to delete
        edge = await afake_chain_edge()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/chains/edges/{edge.id}")

        # Assert the result
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == str(edge.id)
        assert await ChainEdge.objects.filter(id=edge.id).acount() == 0

    async def test_update_non_existent_chain_edge(self, anode_types):
        chain = await afake_chain()
        node1 = await afake_chain_node(chain=chain)
        node2 = await afake_chain_node(chain=chain)
        edge_id = str(uuid4())

        non_existent_edge_id = uuid4()
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
            response = await ac.put(f"/chains/edges/{non_existent_edge_id}", json=data)

        assert response.status_code == 404, response.content


@pytest.mark.django_db
class TestChainGraph:
    async def test_add_chain_edge(self, anode_types):
        chain = await afake_chain()
        node1 = await afake_chain_node(chain=chain)
        node2 = await afake_chain_node(chain=chain)
        await afake_chain_edge(source=node1, target=node2)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/chains/{chain.id}/graph")

        assert response.status_code == 200, response.content
        data = response.json()
        assert data["chain"]["id"] == str(chain.id)
        node_ids = {node["id"] for node in data["nodes"]}
        assert node_ids == {str(node.id) async for node in chain.nodes.all()}
        edge_ids = {edge["id"] for edge in data["edges"]}
        assert edge_ids == {str(edge.id) async for edge in chain.edges.all()}
