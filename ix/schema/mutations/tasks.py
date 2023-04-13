import logging

import graphene
from django.contrib.auth.models import User

from ix.schema.mutations.chat import CreateTaskResponse
from ix.schema.utils import handle_exceptions
from ix.task_log.models import Agent, Task
from ix.task_log.tasks.agent_runner import (
    start_agent_loop,
)


logger = logging.getLogger(__name__)


class GoalInput(graphene.InputObjectType):
    description = graphene.String(required=True)


class CreateTaskInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    goals = graphene.List(GoalInput, required=True)


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

        # TODO: replace with real agent
        name = "iX test bot"
        purpose = "to write python apps"
        agent, _ = Agent.objects.get_or_create(
            name=name, defaults=dict(purpose=purpose)
        )

        for goal in input.goals:
            goal["complete"] = False

        # save to persistence layer
        task = Task.objects.create(
            user=user,
            goals=input.goals,
            name=input.name,
            agent=agent,
        )

        # start task loop
        start_agent_loop.delay(task_id=task.id)

        return CreateTaskResponse(task=task)
