import pytest
from graphene.test import Client
from ix.schema import schema
from ix.task_log.models import TaskLogMessage
from ix.task_log.tests.fake import (
    fake_task,
    fake_user,
    fake_agent,
    fake_command_reply,
    fake_chat,
)

AUTHORIZE_COMMAND_MUTATION = """
    mutation AuthorizeCommand($input: CommandAuthorizeInput!) {
      authorizeCommand(input: $input) {
        taskLogMessage {
          id
          role
          content
          parent {
            id
          }
        }
        errors
      }
    }
"""


ADD_AGENT_MUTATION = """
mutation($chatId: UUID!, $agentId: UUID!) {
    addAgent(chatId: $chatId, agentId: $agentId) {
        chat {
            id
            agents {
                id
            }
        }
    }
}
"""

REMOVE_AGENT_MUTATION = """
mutation($chatId: UUID!, $agentId: UUID!) {
    removeAgent(chatId: $chatId, agentId: $agentId) {
        chat {
            id
            agents {
                id
            }
        }
    }
}
"""

# graphql queries should be in the module scope
CHAT_INPUT_MUTATION = """
    mutation ChatInput($input: ChatInput!) {
      sendInput(input: $input) {
        taskLogMessage {
          id
          role
          content
          parent {
            id
          }
        }
        errors
      }
    }
"""

SEARCH_AGENTS_QUERY = """
query SearchAgentsQuery($search: String!) {
  searchAgents(search: $search) {
    id
    name
  }
}
"""


@pytest.mark.django_db
class TestAuthorizeCommandMutation:
    def test_authorize_command(self, mocker):
        # Create a task, user, agent, and an initial task log message
        task = fake_task()
        fake_user()
        fake_agent()
        responding_to = fake_command_reply(task=task)

        # Mock the Celery task function
        mock_start_agent_loop = mocker.patch(
            "ix.schema.mutations.chat.start_agent_loop"
        )
        client = Client(schema)
        variables = {
            "input": {
                "messageId": str(responding_to.id),
            }
        }

        response = client.execute(AUTHORIZE_COMMAND_MUTATION, variables=variables)

        assert "errors" not in response
        assert response["data"]["authorizeCommand"]["taskLogMessage"]["role"] == "USER"
        assert response["data"]["authorizeCommand"]["taskLogMessage"]["content"] == {
            "type": "AUTHORIZE",
            "message_id": str(responding_to.id),
        }
        assert response["data"]["authorizeCommand"]["errors"] is None

        task_log_message = TaskLogMessage.objects.get(
            pk=response["data"]["authorizeCommand"]["taskLogMessage"]["id"]
        )
        assert task_log_message.task_id == task.id
        assert task_log_message.role == "USER"
        assert task_log_message.content == {
            "type": "AUTHORIZE",
            "message_id": str(responding_to.id),
        }

        mock_start_agent_loop.delay.assert_called_once_with(
            str(responding_to.task_id), message_id=str(task_log_message.id)
        )


@pytest.mark.django_db
class TestChatInputMutation:
    def test_chat_input(self, mocker):
        # Create a task, user, agent, and an initial task log message
        chat = fake_chat()
        fake_user()
        fake_agent()

        client = Client(schema)

        variables = {
            "input": {
                "chatId": str(chat.id),
                "text": "Test input",
            }
        }

        # Mock the Celery task function
        mock_start_agent_loop = mocker.patch(
            "ix.schema.mutations.chat.start_agent_loop"
        )

        response = client.execute(CHAT_INPUT_MUTATION, variables=variables)

        assert "errors" not in response
        assert response["data"]["sendInput"]["taskLogMessage"]["role"] == "USER"
        assert response["data"]["sendInput"]["taskLogMessage"]["content"] == {
            "type": "FEEDBACK",
            "feedback": "Test input",
        }
        assert response["data"]["sendInput"]["errors"] is None

        task_log_message = TaskLogMessage.objects.get(
            pk=response["data"]["sendInput"]["taskLogMessage"]["id"]
        )
        assert task_log_message.task_id == chat.task.id
        assert task_log_message.role == "USER"
        assert task_log_message.content == {
            "type": "FEEDBACK",
            "feedback": "Test input",
        }

        # Assert that the Celery task is dispatched
        mock_start_agent_loop.delay.assert_called_once_with(
            str(chat.task.id),
            str(chat.task.chain.id),
            inputs={"user_input": "Test input", "chat_id": str(chat.id)},
        )

    def test_chat_input_non_existent_chat(self):
        client = Client(schema)
        executed = client.execute(
            CHAT_INPUT_MUTATION,
            variables={"chatId": "non-existent-id", "text": "Test message"},
        )

        assert "errors" in executed

    def test_chat_input_empty_text(self, chat):
        client = Client(schema)
        executed = client.execute(
            CHAT_INPUT_MUTATION, variables={"chatId": str(chat["chat"].id), "text": ""}
        )

        assert "errors" in executed

    def test_chat_input_with_lead_agent(self, chat):
        # Assuming the lead agent has an alias "lead"
        agent = fake_agent()
        chat["chat"].lead = agent
        chat["chat"].save()
        agent.alias = "lead"
        agent.save()

        client = Client(schema)
        executed = client.execute(
            CHAT_INPUT_MUTATION,
            variables={
                "input": {
                    "chatId": str(chat["chat"].id),
                    "text": "@lead Message for lead",
                }
            },
        )

        assert "errors" not in executed
        assert (
            executed["data"]["sendInput"]["taskLogMessage"]["content"]["feedback"]
            == "@lead Message for lead"
        )

    def test_chat_input_with_other_agent(self, chat):
        # Assuming the other agent has an alias "other"
        agent = fake_agent()
        chat["chat"].agents.add(agent)
        agent.alias = "other"
        agent.save()

        client = Client(schema)
        executed = client.execute(
            CHAT_INPUT_MUTATION,
            variables={
                "input": {
                    "chatId": str(chat["chat"].id),
                    "text": "@other Message for other",
                }
            },
        )

        assert "errors" not in executed
        assert (
            executed["data"]["sendInput"]["taskLogMessage"]["content"]["feedback"]
            == "@other Message for other"
        )


@pytest.mark.django_db
class TestAddRemoveAgentMutation:
    def test_add_remove_agent(self, chat):
        agent = fake_agent()

        # First, add the agent to the chat.
        client = Client(schema)
        client.execute(
            ADD_AGENT_MUTATION,
            variables={"chatId": str(chat["chat"].id), "agentId": str(agent.id)},
        )

        assert chat["chat"].agents.filter(id=agent.id).exists()

        # Then, remove the agent.
        executed = client.execute(
            REMOVE_AGENT_MUTATION,
            variables={"chatId": str(chat["chat"].id), "agentId": str(agent.id)},
        )

        assert chat["chat"].agents.filter(id=agent.id).exists() is False
        assert "errors" not in executed
        assert executed["data"]["removeAgent"]["chat"]["id"] == str(chat["chat"].id)
        assert str(agent.id) not in [
            agent["id"] for agent in executed["data"]["removeAgent"]["chat"]["agents"]
        ]

    def test_add_agent_when_agent_is_lead(self, chat):
        agent = fake_agent()
        chat["chat"].lead = agent
        chat["chat"].save()

        assert chat["chat"].agents.count() == 2

        variables = {"chatId": str(chat["chat"].id), "agentId": str(agent.id)}

        # Execute mutation
        result = schema.execute(ADD_AGENT_MUTATION, variable_values=variables)

        # Assert that the agent was not added to the agents list
        assert not result.errors
        assert len(result.data["addAgent"]["chat"]["agents"]) == 2
        assert chat["chat"].agents.count() == 2

    def test_add_agent_when_agent_is_already_in_chat(self, chat):
        agent = fake_agent()
        chat["chat"].agents.add(agent)
        chat["chat"].save()
        assert chat["chat"].agents.count() == 3
        assert chat["chat"].agents.filter(pk=agent.id).exists()

        variables = {"chatId": str(chat["chat"].id), "agentId": str(agent.id)}

        # Execute mutation
        result = schema.execute(ADD_AGENT_MUTATION, variable_values=variables)

        # Assert that the agent was not added again to the agents list
        assert not result.errors
        assert len(result.data["addAgent"]["chat"]["agents"]) == 3
        assert chat["chat"].agents.count() == 3
        assert chat["chat"].agents.filter(pk=agent.id).exists()


@pytest.mark.django_db
class TestSearchAgents:
    @pytest.fixture(autouse=True)
    def setup(self, chat):
        self.client = Client(schema)
        self.chat = chat["chat"]
        self.agents = [fake_agent() for _ in range(3)]

    def test_search_agents(self):
        for agent in self.agents:
            self.chat.agents.add(agent)

        result = self.client.execute(
            SEARCH_AGENTS_QUERY, variables={"search": self.agents[0].name}
        )

        assert "errors" not in result
        assert len(result["data"]["searchAgents"]) == 1
        assert result["data"]["searchAgents"][0]["id"] == str(self.agents[0].id)

    def test_search_agents_no_match(self):
        result = self.client.execute(
            SEARCH_AGENTS_QUERY, variables={"search": "nonexistent"}
        )

        assert "errors" not in result
        assert len(result["data"]["searchAgents"]) == 0
