import pytest
from graphene.test import Client
from ix.schema import schema
from ix.task_log.models import TaskLogMessage
from ix.task_log.tests.fake import fake_task, fake_user, fake_agent, fake_command_reply


AUTHORIZE_COMMAND_MUTATION = """
    mutation AuthorizeCommand($input: CommandAuthorizeInput!) {
      authorizeCommand(input: $input) {
        taskLogMessage {
          id
          role
          content {
            ... on AuthorizeContentType {
              type
              messageId
            }
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
                "messageId": responding_to.id,
            }
        }

        response = client.execute(AUTHORIZE_COMMAND_MUTATION, variables=variables)

        assert "errors" not in response
        assert response["data"]["authorizeCommand"]["taskLogMessage"]["role"] == "USER"
        assert response["data"]["authorizeCommand"]["taskLogMessage"]["content"] == {
            "type": "AUTHORIZE",
            "messageId": str(responding_to.id),
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

        mock_start_agent_loop.delay.assert_called_once_with(responding_to.task_id)


# graphql queries should be in the module scope
TASK_FEEDBACK_MUTATION = """
    mutation TaskFeedback($input: TaskFeedbackInput!) {
      sendFeedback(input: $input) {
        taskLogMessage {
          id
          role
          content {
            ... on FeedbackContentType {
              type
              feedback
            }
          }
        }
        errors
      }
    }
"""


@pytest.mark.django_db
class TestTaskFeedbackMutation:
    def test_task_feedback(self, mocker):
        # Create a task, user, agent, and an initial task log message
        task = fake_task()
        fake_user()
        fake_agent()

        client = Client(schema)

        variables = {
            "input": {
                "taskId": task.id,
                "feedback": "Test feedback",
            }
        }

        # Mock the Celery task function
        mock_start_agent_loop = mocker.patch(
            "ix.schema.mutations.chat.start_agent_loop"
        )

        response = client.execute(TASK_FEEDBACK_MUTATION, variables=variables)

        print(response)

        assert "errors" not in response
        assert response["data"]["sendFeedback"]["taskLogMessage"]["role"] == "USER"
        assert response["data"]["sendFeedback"]["taskLogMessage"]["content"] == {
            "type": "FEEDBACK",
            "feedback": "Test feedback",
        }
        assert response["data"]["sendFeedback"]["errors"] is None

        task_log_message = TaskLogMessage.objects.get(
            pk=response["data"]["sendFeedback"]["taskLogMessage"]["id"]
        )
        assert task_log_message.task_id == task.id
        assert task_log_message.role == "USER"
        assert task_log_message.content == {
            "type": "FEEDBACK",
            "feedback": "Test feedback",
        }

        # Assert that the Celery task is dispatched
        mock_start_agent_loop.delay.assert_called_once_with(str(task.id))
