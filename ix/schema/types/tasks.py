import logging

import graphene
from graphene_django import DjangoObjectType

from ix.task_log.models import Task


logger = logging.getLogger(__name__)


class GoalType(graphene.ObjectType):
    description = graphene.String(required=True)
    complete = graphene.Boolean(required=True)


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = "__all__"

    goals = graphene.List(GoalType)

    def resolve_goals(self, info):
        if self.goals is not None:
            return [
                GoalType(description=goal["description"], complete=goal["complete"])
                for goal in self.goals
            ]
        return None
