import pytest
from graphene.test import Client
from ix.schema import schema

from ix.task_log.tests.fake import fake_chat, fake_agent

AGENT_SEARCH = """
   query SearchAgentsQuery($search: String, $chatId: UUID) {
    searchAgents(search: $search, chatId: $chatId) {
      id
      name
      alias
      purpose
      chain {
        id
        name
        description
      }
    }
  }
"""


@pytest.mark.django_db
@pytest.mark.usefixtures("node_types")
class TestAgentSearch:
    @pytest.mark.parametrize(
        "pattern,expected_names",
        [
            ["agent 1", ["agent 1"]],
            ["agent", ["agent 1", "agent 2"]],
            ["1", ["agent 1"]],
            ["one", ["agent 1"]],
            ["age", ["agent 1", "agent 2"]],
        ],
    )
    def test_agent_search_name(self, pattern, expected_names):
        """Test basic search"""
        fake_agent(name="agent 1", alias="one")
        fake_agent(name="agent 2", alias="two")

        variables = {
            "search": pattern,
        }

        client = Client(schema)
        response = client.execute(AGENT_SEARCH, variables=variables)

        assert "errors" not in response
        assert len(response["data"]["searchAgents"]) == len(expected_names)
        for i in range(len(expected_names)):
            assert response["data"]["searchAgents"][i]["name"] in expected_names

    def test_filter_chat(self):
        """Test chat filter"""
        agent1 = fake_agent(name="agent 1", alias="one")
        agent2 = fake_agent(name="agent 2", alias="two")
        fake_agent(name="agent 3", alias="three")
        chat = fake_chat()
        chat.agents.set([agent1, agent2])
        client = Client(schema)

        def query(search):
            variables = {
                "chatId": str(chat.id),
                "search": search,
            }

            return client.execute(AGENT_SEARCH, variables=variables)

        response = query("agent 3")
        assert "errors" not in response
        assert len(response["data"]["searchAgents"]) == 0

        response = query("agent 1")
        assert "errors" not in response
        assert len(response["data"]["searchAgents"]) == 1

    @pytest.mark.skip("user auth not implemented yet")
    def test_chat_is_not_users(self):
        """Raise a 403 if the user does not have access to the chat they are trying to search"""
        raise NotImplementedError
