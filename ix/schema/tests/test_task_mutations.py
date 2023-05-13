import pytest
from graphene.test import Client
from ix.schema import schema
from ix.task_log.models import TaskLogMessage, Task
from ix.task_log.tests.fake import fake_task, fake_user, fake_agent


@pytest.mark.django_db
class TestSetTaskAutonomousMutation:
    def test_set_task_autonomous(self):
        task = fake_task()
        client = Client(schema)

        mutation = """
            mutation SetTaskAutonomous($taskId: UUID!, $autonomous: Boolean!) {
              setTaskAutonomous(taskId: $taskId, autonomous: $autonomous) {
                task {
                  id
                  autonomous
                }
              }
            }
        """

        variables = {"taskId": str(task.id), "autonomous": False}

        response = client.execute(mutation, variables=variables)

        task.refresh_from_db()

        assert "errors" not in response
        assert response["data"]["setTaskAutonomous"]["task"]["id"] == str(task.id)
        assert (
            response["data"]["setTaskAutonomous"]["task"]["autonomous"]
            == task.autonomous
        )
        assert task.autonomous is False

        log_message = TaskLogMessage.objects.get(task=task)
        assert log_message.role == "user"
        assert log_message.content["enabled"] == task.autonomous


CREATE_TASK_MUTATION = """
    mutation CreateTask($input: CreateTaskInput!) {
      createTask(input: $input) {
        task {
          id
          name
          autonomous
          agent {
            id
          }
        }
      }
    }
"""


@pytest.mark.django_db
class TestCreateTaskMutation:
    def test_create_task_without_agent_autonomous_flag(self):
        fake_user()
        fake_agent(pk=1)
        client = Client(schema)

        variables = {
            "input": {
                "name": "Test Task",
                "autonomous": False,
            }
        }

        response = client.execute(CREATE_TASK_MUTATION, variables=variables)

        assert "errors" not in response, response["errors"]
        assert response["data"]["createTask"]["task"]["name"] == "Test Task"
        assert response["data"]["createTask"]["task"]["agent"]["id"]
        task = Task.objects.get(pk=response["data"]["createTask"]["task"]["id"])
        assert task.autonomous is False

    def test_create_task_with_autonomous_flag(self):
        fake_user()
        agent = fake_agent()
        client = Client(schema)

        variables = {
            "input": {
                "name": "Test Task",
                "agentId": str(agent.id),
                "autonomous": True,
            }
        }

        response = client.execute(CREATE_TASK_MUTATION, variables=variables)

        assert "errors" not in response
        assert response["data"]["createTask"]["task"]["name"] == "Test Task"
        assert response["data"]["createTask"]["task"]["agent"]["id"] == str(agent.id)
        task = Task.objects.get(pk=response["data"]["createTask"]["task"]["id"])
        assert task.autonomous is True
