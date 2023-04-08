import graphene
from graphene_django import DjangoObjectType
from .models import Agent, Task, TaskLogMessage


class AgentType(DjangoObjectType):
    class Meta:
        model = Agent
        fields = "__all__"


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = "__all__"


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


schema = graphene.Schema(query=Query)
