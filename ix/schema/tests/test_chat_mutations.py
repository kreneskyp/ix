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
