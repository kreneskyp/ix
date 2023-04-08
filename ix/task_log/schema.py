import graphene
from graphene_django import DjangoObjectType

from ix.task_log.models import Agent, Task, TaskLogMessage


class AgentType(DjangoObjectType):
    class Meta:
        model = Agent
        fields = "__all__"


class GoalType(graphene.ObjectType):
    name = graphene.String(required=True)
    description = graphene.String(required=True)
    complete = graphene.Boolean(required=True)


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = "__all__"

    goals = graphene.List(GoalType)


class TaskLogMessageType(DjangoObjectType):
    class Meta:
        model = TaskLogMessage
        fields = "__all__"


class Query(graphene.ObjectType):
    agents = graphene.List(AgentType)
    tasks = graphene.List(TaskType)
    task_log_messages = graphene.List(
        TaskLogMessageType, task_id=graphene.ID(required=True)
    )
    task = graphene.Field(TaskType, id=graphene.ID(required=True))

    def resolve_task(self, info, id):
        return Task.objects.get(pk=id)

    def resolve_agents(self, info):
        return Agent.objects.all()

    def resolve_tasks(self, info):
        return Task.objects.select_related("user").all()

    def resolve_task_log_messages(self, info, task_id):
        return TaskLogMessage.objects.filter(task_id=task_id).select_related("agent")


class TaskLogResponseInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    response = graphene.String(required=True)
    is_authorized = graphene.Boolean(required=True)


class TaskLogMessageResponse(graphene.ObjectType):
    task_log_message = graphene.Field(TaskLogMessage)
    errors = graphene.List(graphene.String)

    def resolve_task_log(root, info):
        return root.task_log


class RespondToTaskLogMutation(graphene.Mutation):
    class Arguments:
        input = TaskLogResponseInput(required=True)

    task_log_message = graphene.Field(TaskLogMessageType)
    errors = graphene.Field(graphene.List(graphene.String))

    @staticmethod
    def mutate(root, info, input):
        message_id = input.id
        response = input.response
        is_authorized = input.is_authorized

        message = TaskLogMessage.objects.get(id=message_id)
        message.user_response = response
        message.is_authorized = is_authorized
        message.save()

        return TaskLogMessageResponse(task_log_message=message)


class Mutation(graphene.ObjectType):
    respond_to_task_msg = RespondToTaskLogMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
