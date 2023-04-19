import logging

import graphene
from django.contrib.auth.models import User

from ix.schema.types.tasks import TaskType
from ix.schema.utils import handle_exceptions
from ix.task_log.models import Agent, Task, TaskLogMessage
from ix.task_log.tasks.agent_runner import (
    start_agent_loop,
)


logger = logging.getLogger(__name__)


class CreateTaskResponse(graphene.ObjectType):
    task = graphene.Field(TaskType)


class GoalInput(graphene.InputObjectType):
    description = graphene.String(required=True)


class CreateTaskInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    goals = graphene.List(GoalInput)
    agent_id = graphene.UUID()
    autonomous = graphene.Boolean()


class CreateTaskMutation(graphene.Mutation):
    Output = CreateTaskResponse

    class Arguments:
        input = CreateTaskInput(required=True)

    @staticmethod
    @handle_exceptions
    def mutate(root, info, input):
        user = User.objects.latest("id")

        # TODO: turn this on once auth is setup for UI
        # user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication is required to create a task.")

        # If agent is not provided, use the default agent
        if input.agent_id:
            agent = Agent.objects.get(pk=input.agent_id)
        else:
            agent = Agent.objects.get(pk=1)

        if input.goals:
            for goal in input.goals:
                goal["complete"] = False

        # Save to persistence layer
        task = Task.objects.create(
            user=user,
            goals=input.goals or [],
            name=input.name,
            agent=agent,
            autonomous=input.autonomous if input.autonomous is not None else True,
        )

        # Start task loop
        start_agent_loop.delay(task_id=task.id)

        return CreateTaskResponse(task=task)


class SetTaskAutonomousMutation(graphene.Mutation):
    task = graphene.Field(TaskType)

    class Arguments:
        task_id = graphene.UUID(required=True)
        autonomous = graphene.Boolean(required=True)

    @handle_exceptions
    def mutate(self, info, task_id, autonomous):
        task = Task.objects.get(pk=task_id)

        # save to task
        task.autonomous = autonomous
        task.save()

        # log message
        TaskLogMessage.objects.create(
            task=task,
            role="user",
            content={"type": "AUTONOMOUS", "enabled": task.autonomous},
        )

        return SetTaskAutonomousMutation(task=task)
