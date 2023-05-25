import logging

import graphene
from django.db.models import Q
from graphene.types.generic import GenericScalar
from graphene_django import DjangoObjectType

from ix.task_log.models import Task, Artifact, Plan, PlanSteps

logger = logging.getLogger(__name__)


class GoalType(graphene.ObjectType):
    description = graphene.String(required=True)
    complete = graphene.Boolean(required=True)


class PlanType(DjangoObjectType):
    class Meta:
        model = Plan
        fields = "__all__"


class StepType(DjangoObjectType):
    class Meta:
        model = PlanSteps
        fields = "__all__"


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = "__all__"

    created_plans = graphene.Field(
        graphene.List(PlanType), is_draft=graphene.Boolean(required=False)
    )

    def resolve_created_plans(self, info, is_draft=None):
        if is_draft is None:
            return self.created_plans.all()
        else:
            return self.created_plans.filter(is_draft=is_draft)


class ArtifactType(DjangoObjectType):
    storage = GenericScalar()

    class Meta:
        model = Artifact
        fields = "__all__"


class Query(graphene.ObjectType):
    search_artifacts = graphene.List(
        ArtifactType, search=graphene.String(), chat_id=graphene.UUID()
    )

    def resolve_search_artifacts(self, info, search):
        # basic search for now, add pg_vector similarity search later

        return (
            Artifact.objects.filter(
                Q(name__icontains=search) | Q(key__icontains=search)
            )
            .order_by("key", "-created_at")
            .distinct("key")
        )
