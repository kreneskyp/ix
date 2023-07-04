import pytest
import uuid
from graphene.test import Client

from ix.chains.models import ChainEdge, ChainNode, Chain
from ix.chains.tests.mock_chain import MOCK_CHAIN_CONFIG
from ix.schema import schema
from ix.task_log.tests.fake import fake_chain_node, fake_chain_edge, fake_chain

ADD_CHAIN_NODE = """
    mutation AddChainNode($data: ChainNodeInput!) {
        addChainNode(data: $data) {
            node {
                id
                classPath
                config
                name
                description
                position {
                    x
                    y
                }
                chain {
                  id
                }
            }
        }
    }
"""

UPDATE_CHAIN_NODE = """
    mutation UpdateChainNode($data: ChainNodeInput!) {
        updateChainNode(data: $data) {
            node {
                id
                classPath
                config
                name
                description
                position {
                    x
                    y
                }
            }
        }
    }
"""

UPDATE_CHAIN_NODE_POSITION = """
    mutation UpdateChainNodePosition($data: ChainNodePositionInput!) {
        updateChainNodePosition(data: $data) {
            node {
                id
                position {
                    x
                    y
                }
            }
        }
    }
"""

DELETE_CHAIN_NODE = """
    mutation DeleteChainNode($id: UUID!) {
        deleteChainNode(id: $id) {
            node {
                id
            }
            edges {
                id
            }
        }
    }
"""

ADD_CHAIN_EDGE = """
    mutation AddChainEdge($data: ChainEdgeInput!) {
        addChainEdge(data: $data) {
            edge {
                id
                key
                inputMap
                source {
                  id
                }
                target {
                  id
                }
            }
        }
    }
"""

UPDATE_CHAIN_EDGE = """
    mutation UpdateChainEdge($data: ChainEdgeInput!) {
        updateChainEdge(data: $data) {
            edge {
                id
                key
                inputMap
                source {
                  id
                }
                target {
                  id
                }
            }
        }
    }
"""

DELETE_CHAIN_EDGE = """
    mutation DeleteChainEdge($id: UUID!) {
        deleteChainEdge(id: $id) {
            edge {
                id
            }
        }
    }
"""


@pytest.mark.django_db
@pytest.mark.usefixtures("node_types")
class TestChainNodeMutation:
    def test_add_first_chain_node_mutation(self):
        """
        The first node will create the chain
        """
        # Create a Graphene client
        client = Client(schema)

        assert not Chain.objects.filter(name="Custom Node").exists()

        # Prepare variables for the GraphQL query
        # exclude chain here
        variables = {
            "data": {
                "classPath": "ix.chains.llm_chain.LLMChain",
                "config": {},
                "name": "Custom Node",
                "description": "Custom Description",
                "position": {
                    "x": 10,
                    "y": 20,
                },
            }
        }

        # Execute the GraphQL query
        result = client.execute(ADD_CHAIN_NODE, variables=variables)

        # Assert the result
        assert "errors" not in result
        node_data = result["data"]["addChainNode"]["node"]
        assert node_data["id"] is not None
        assert node_data["name"] == "Custom Node"
        assert node_data["description"] == "Custom Description"
        assert node_data["position"] == {
            "x": 10,
            "y": 20,
        }

        # assert models
        node = ChainNode.objects.get(id=node_data["id"])
        assert node.chain_id is not None

    def test_add_chain_node_mutation(self):
        """
        subsequent nodes will use the existing chain
        """
        # Create a Graphene client
        client = Client(schema)

        chain = fake_chain()

        # Prepare variables for the GraphQL query
        variables = {
            "data": {
                "chainId": str(chain.id),
                "classPath": "ix.chains.llm_chain.LLMChain",
                "config": {},
                "name": "Custom Node",
                "description": "Custom Description",
                "position": {
                    "x": 10,
                    "y": 20,
                },
            }
        }

        # Execute the GraphQL query
        result = client.execute(ADD_CHAIN_NODE, variables=variables)

        # Assert the result
        assert "errors" not in result
        node_data = result["data"]["addChainNode"]["node"]
        assert node_data["id"] is not None
        assert node_data["name"] == "Custom Node"
        assert node_data["description"] == "Custom Description"
        assert node_data["position"] == {
            "x": 10,
            "y": 20,
        }

        # assert models
        node = ChainNode.objects.get(id=node_data["id"])
        assert node.chain_id == chain.id

    def test_update_chain_node_mutation(self):
        # Create a Graphene client
        client = Client(schema)

        # Create a chain node to update
        node = fake_chain_node()

        # Prepare variables for the GraphQL query
        variables = {
            "data": {
                "id": str(node.id),
                "classPath": "custom_class_path",
                "name": "Updated Node",
                "description": "Updated Description",
                "position": {
                    "x": 10,
                    "y": 20,
                },
            }
        }

        # Execute the GraphQL query
        result = client.execute(UPDATE_CHAIN_NODE, variables=variables)

        # Assert the result
        assert "errors" not in result
        node_data = result["data"]["updateChainNode"]["node"]
        assert node_data["id"] == str(node.id)
        assert node_data["name"] == "Updated Node"
        assert node_data["description"] == "Updated Description"
        assert node_data["position"] == {
            "x": 10,
            "y": 20,
        }

    def test_delete_chain_node_mutation(self):
        # Create a Graphene client
        client = Client(schema)

        # Create a chain node to delete
        node = fake_chain_node(config=MOCK_CHAIN_CONFIG)
        source_node = fake_chain_node(chain=node.chain, config=MOCK_CHAIN_CONFIG)
        target_node = fake_chain_node(chain=node.chain, config=MOCK_CHAIN_CONFIG)
        edge_in = fake_chain_edge(source=source_node, target=node)
        edge_out = fake_chain_edge(source=node, target=target_node)

        # Prepare variables for the GraphQL query
        variables = {"id": str(node.id)}

        # Execute the GraphQL query
        result = client.execute(DELETE_CHAIN_NODE, variables=variables)

        # Assert the result
        # Node and edges should be removed
        assert "errors" not in result
        assert result["data"]["deleteChainNode"]["node"]["id"] == str(node.id)
        edges = result["data"]["deleteChainNode"]["edges"]
        assert len(edges) == 2
        assert edges[0]["id"] in {str(edge_in.id), str(edge_out.id)}
        assert edges[1]["id"] in {str(edge_in.id), str(edge_out.id)}

        # Node and edges should be removed from db
        assert ChainNode.objects.filter(id=node.id).count() == 0
        assert ChainEdge.objects.filter(id=edge_in.id).count() == 0
        assert ChainEdge.objects.filter(id=edge_out.id).count() == 0


@pytest.mark.django_db
@pytest.mark.usefixtures("node_types")
class TestChainNodePositionMutation:
    def test_update_position(self):
        """
        The first node will create the chain
        """
        # Create a Graphene client
        client = Client(schema)

        assert not Chain.objects.filter(name="Custom Node").exists()

        node = fake_chain_node()

        # Prepare variables for the GraphQL query
        # exclude chain here
        variables = {
            "data": {
                "id": str(node.id),
                "position": {
                    "x": 100,
                    "y": 200,
                },
            }
        }

        # Execute the GraphQL query
        result = client.execute(UPDATE_CHAIN_NODE_POSITION, variables=variables)

        # Assert the result
        assert "errors" not in result
        node_data = result["data"]["updateChainNodePosition"]["node"]
        assert node_data["id"] is not None
        assert node_data["position"] == {
            "x": 100,
            "y": 200,
        }


@pytest.mark.django_db
@pytest.mark.usefixtures("node_types")
class TestChainEdgeMutation:
    def test_add_chain_edge_mutation(self):
        # Create a Graphene client
        client = Client(schema)

        chain = fake_chain()
        node1 = fake_chain_node(chain=chain)
        node2 = fake_chain_node(chain=chain)
        edge_id = uuid.uuid4()

        # Prepare variables for the GraphQL query
        variables = {
            "data": {
                "id": str(edge_id),
                "sourceId": str(node1.id),
                "targetId": str(node2.id),
                "key": "Custom Key",
                "chainId": str(chain.id),
                "inputMap": {},
            }
        }

        # Execute the GraphQL query
        result = client.execute(ADD_CHAIN_EDGE, variables=variables)

        # Assert the result
        assert "errors" not in result
        edge_data = result["data"]["addChainEdge"]["edge"]
        assert edge_data["id"] == str(edge_id)
        assert edge_data["source"] == {"id": str(node1.id)}
        assert edge_data["target"] == {"id": str(node2.id)}
        assert edge_data["key"] == "Custom Key"
        assert edge_data["inputMap"] == {}

    def test_update_chain_edge_mutation(self):
        # Create a Graphene client
        client = Client(schema)

        # Create a chain edge to update
        edge = fake_chain_edge()

        # Prepare variables for the GraphQL query
        variables = {
            "data": {
                "id": str(edge.id),
                "key": "Updated Key",
                "inputMap": {"param1": "value1", "param2": "value2"},
                "sourceId": str(edge.source_id),
                "targetId": str(edge.target_id),
            }
        }

        # Execute the GraphQL query
        result = client.execute(UPDATE_CHAIN_EDGE, variables=variables)

        # Assert the result
        assert "errors" not in result
        edge_data = result["data"]["updateChainEdge"]["edge"]
        assert edge_data["id"] == str(edge.id)
        assert edge_data["key"] == "Updated Key"
        assert edge_data["inputMap"] == {"param1": "value1", "param2": "value2"}

    def test_delete_chain_edge_mutation(self):
        client = Client(schema)

        # Create a chain edge to delete
        edge = fake_chain_edge()

        # Prepare variables for the GraphQL query
        variables = {"id": str(edge.id)}

        # Execute the GraphQL query
        result = client.execute(DELETE_CHAIN_EDGE, variables=variables)

        # Assert the result
        assert "errors" not in result
        assert result["data"]["deleteChainEdge"]["edge"]["id"] == str(edge.id)
        assert ChainEdge.objects.filter(id=edge.id).count() == 0
