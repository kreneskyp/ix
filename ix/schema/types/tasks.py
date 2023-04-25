import logging

import graphene
from graphene_django import DjangoObjectType

from ix.task_log.models import Task, Artifact, Plan, PlanSteps

logger = logging.getLogger(__name__)


class GoalType(graphene.ObjectType):
    description = graphene.String(required=True)
    complete = graphene.Boolean(required=True)


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = "__all__"

    goals = graphene.List(GoalType)


class ArtifactType(DjangoObjectType):
    class Meta:
        model = Artifact
        fields = "__all__"


class PlanType(DjangoObjectType):
    class Meta:
        model = Plan
        fields = "__all__"


class StepType(DjangoObjectType):
    class Meta:
        model = PlanSteps
        fields = "__all__"
