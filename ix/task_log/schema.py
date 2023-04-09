import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User

from ix.task_log.models import Agent, Task, TaskLogMessage
from ix.task_log.tasks.agent_runner import resume_agent_loop_with_feedback, start_agent_loop

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"

class AgentType(DjangoObjectType):
    class Meta:
        model = Agent
        fields = "__all__"


class GoalType(graphene.ObjectType):
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
    users = graphene.List(UserType)
    agents = graphene.List(AgentType)
    tasks = graphene.List(TaskType)
    task_log_messages = graphene.List(
        TaskLogMessageType, task_id=graphene.ID(required=True)
    )
    user = graphene.Field(UserType, id=graphene.ID(required=True))
    agent = graphene.Field(AgentType, id=graphene.ID(required=True))
    task = graphene.Field(TaskType, id=graphene.ID(required=True))

    def resolve_user(self, info, id):
        return User.objects.get(pk=id)

    def resolve_agent(self, info, id):
        return Agent.objects.get(pk=id)

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


class GoalInput(graphene.InputObjectType):
    description = graphene.String(required=True)


class CreateTaskInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    goals = graphene.List(GoalInput, required=True)


class CreateTaskResponse(graphene.ObjectType):
    task = graphene.Field(TaskType)
    errors = graphene.List(graphene.String)
class CreateTaskMutation(graphene.Mutation):
    task = graphene.Field(TaskType)

    class Arguments:
        input = CreateTaskInput(required=True)

    @staticmethod
    def mutate(root, info, input):

        print ("ASDFASDFASDF")

        user = User.objects.latest('id')
        print("ASasdfasdfasdfasdfDFASDFASDF")
        # TODO: turn this on once auth is setup for UI
        #user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication is required to create a task.")
        print("222ASDFASDFASDF")
        # TODO: replace with real agent
        name = "iX test bot"
        purpose = "to write python apps"
        agent = Agent.objects.create(
            name=name,
            purpose=purpose,
        )

        print("124312341234ASDFASDFASDF")

        print("111ASDFASDFASDF")
        # save to persistence layer
        task = Task.objects.create(
            user=user,
            goals=input.goals,
            name=input.name,
            agent=agent,
        )
        print("123ASDFASDFASDF")
        # start task loop
        #start_agent_loop.apply_async()

        wtf = CreateTaskResponse(task=task)
        return wtf


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

        # save to persistent storage
        message = TaskLogMessage.objects.get(id=message_id)
        message.user_response = response
        message.is_authorized = is_authorized
        message.save()

        # resume task loop
        resume_agent_loop_with_feedback.apply_async(message_id=message_id)

        return TaskLogMessageResponse(task_log_message=message)


class Mutation(graphene.ObjectType):
    create_task = CreateTaskMutation.Field()
    respond_to_task_msg = RespondToTaskLogMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

