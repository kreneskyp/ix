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
            mutation SetTaskAutonomous($taskId: ID!, $autonomous: Boolean!) {
              setTaskAutonomous(taskId: $taskId, autonomous: $autonomous) {
                task {
                  id
                  autonomous
                }
              }
            }
        """

        variables = {
            "taskId": task.id,
            "autonomous": False
        }

        response = client.execute(mutation, variables=variables)

        task.refresh_from_db()

        assert "errors" not in response
        assert response["data"]["setTaskAutonomous"]["task"]["id"] == str(task.id)
        assert response["data"]["setTaskAutonomous"]["task"]["autonomous"] == task.autonomous
        assert task.autonomous == False

        log_message = TaskLogMessage.objects.get(task=task)
        assert log_message.role == 'user'
        assert log_message.content['enabled'] == task.autonomous

