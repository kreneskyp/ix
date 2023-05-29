import logging
import graphene
from django.contrib.auth.models import User
from django.db.models import Q

from ix.schema.subscriptions import Subscription as ChatSubscription
from ix.schema.mutations.chat import Mutation as ChatMutation
from ix.schema.mutations.tasks import Mutation as TaskMutation
from ix.schema.mutations.agents import Mutation as AgentMutation
from ix.schema.types.chat import Query as ChatQuery
from ix.schema.types.agents import Query as AgentQuery
from ix.schema.types.chains import Query as ChainQuery
from ix.schema.types.tasks import Query as TaskQuery
from ix.schema.types.auth import UserType
from ix.schema.types.messages import TaskLogMessageType
from ix.schema.types.tasks import TaskType
from ix.task_log.models import Task, TaskLogMessage

logger = logging.getLogger(__name__)


class Query(ChainQuery, ChatQuery, AgentQuery, TaskQuery, graphene.ObjectType):
    """
    Aggregation of graphql queries
    """

    users = graphene.List(UserType)
    tasks = graphene.List(TaskType)
    task_log_messages = graphene.List(
        TaskLogMessageType, task_id=graphene.UUID(required=True)
    )
    user = graphene.Field(UserType, id=graphene.ID(required=True))
    task = graphene.Field(TaskType, id=graphene.UUID(required=True))

    def resolve_user(self, info, id):
        return User.objects.get(pk=id)

    def resolve_task(self, info, id):
        return Task.objects.get(pk=id)

    def resolve_tasks(self, info):
        return Task.objects.select_related("user").all()

    def resolve_task_log_messages(self, info, task_id):
        return TaskLogMessage.objects.filter(
            Q(task_id=task_id) | Q(task__parent_id=task_id)
        ).select_related("agent")


class Subscription(ChatSubscription, graphene.ObjectType):
    """
    Aggregation of graphql subscriptions
    """


class Mutation(AgentMutation, TaskMutation, ChatMutation, graphene.ObjectType):
    """
    Aggregation of graphql mutations
    """


# full graphql schema
schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)


__all__ = ["schema", "Query", "Mutation"]
