import logging
import graphene

from ix.schema.subscriptions import Subscription as ChatSubscription
from ix.schema.types.tasks import TaskType
from ix.task_log.models import Task

logger = logging.getLogger(__name__)


class Query(graphene.ObjectType):
    """
    Aggregation of graphql queries
    """

    tasks = graphene.List(TaskType)
    task = graphene.Field(TaskType, id=graphene.UUID(required=True))

    def resolve_task(self, info, id):
        return Task.objects.get(pk=id)

    def resolve_tasks(self, info):
        return Task.objects.select_related("user").all()


class Subscription(ChatSubscription, graphene.ObjectType):
    """
    Aggregation of graphql subscriptions
    """


# full graphql schema
schema = graphene.Schema(query=Query, subscription=Subscription)


__all__ = ["schema", "Query"]
