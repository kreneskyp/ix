import logging
import graphene
import re
from django.contrib.auth.models import User
from django.db.models import Q

from ix.agents.models import Agent
from ix.chains.management.commands.create_coder_v1 import CODER_V1_AGENT
from ix.chains.management.commands.create_coder_v2 import CODER_V2_AGENT
from ix.chains.management.commands.create_ix_v2 import IX_AGENT_V2
from ix.chat.models import Chat
from ix.schema.types.chat import ChatType
from ix.schema.types.messages import TaskLogMessageType
from ix.schema.utils import handle_exceptions
from ix.task_log.models import TaskLogMessage, UserFeedback, Task
from ix.task_log.tasks.agent_runner import (
    start_agent_loop,
)


logger = logging.getLogger(__name__)


class ChatMutationResponse(graphene.ObjectType):
    chat = graphene.Field(ChatType)


class CreateChatInput(graphene.InputObjectType):
    name = graphene.String(required=False)
    agent_id = graphene.UUID(required=False)


class CreateChatMutation(graphene.Mutation):
    Output = ChatMutationResponse

    class Arguments:
        input = CreateChatInput(required=False)

    @staticmethod
    @handle_exceptions
    def mutate(root, info, input=None):
        user = User.objects.latest("id")

        # TODO: turn this on once auth is setup for UI
        # user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication is required to create a task.")

        # If agent is not provided, use the default agent
        if input and input.agent_id:
            lead = Agent.objects.get(pk=input.agent_id)
        else:
            lead = Agent.objects.get(pk=IX_AGENT_V2)

        # spawn subtask
        task = Task.objects.create(
            user=user,
            name=input and input.name or "",
            agent=lead,
            chain=lead.chain,
            autonomous=input.autonomous
            if (input and input.autonomous is not None)
            else True,
        )

        chat = Chat.objects.create(
            task=task,
            lead=lead,
        )

        code = Agent.objects.get(id=CODER_V2_AGENT)
        chat.agents.add(code)

        return ChatMutationResponse(chat=chat)


class RemoveAgentMutation(graphene.Mutation):
    class Arguments:
        agent_id = graphene.UUID(required=True)
        chat_id = graphene.UUID(required=True)

    chat = graphene.Field(ChatType)

    @staticmethod
    def mutate(root, info, agent_id, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
            agent = Agent.objects.get(id=agent_id)
            chat.agents.remove(agent)
            return RemoveAgentMutation(chat=chat)
        except Chat.DoesNotExist:
            raise graphene.GraphQLError("Chat does not exist.")
        except Agent.DoesNotExist:
            raise graphene.GraphQLError("Agent does not exist.")


class AddAgentMutation(graphene.Mutation):
    class Arguments:
        agent_id = graphene.UUID(required=True)
        chat_id = graphene.UUID(required=True)

    chat = graphene.Field(ChatType)

    @staticmethod
    def mutate(root, info, agent_id, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
            agent = Agent.objects.get(id=agent_id)

            # Check if the agent is already a lead or an agent
            if chat.lead == agent or chat.agents.filter(id=agent_id).exists():
                return AddAgentMutation(chat=chat)

            chat.agents.add(agent)
            chat.save()

            return AddAgentMutation(chat=chat)
        except Chat.DoesNotExist:
            raise graphene.GraphQLError("Chat does not exist.")
        except Agent.DoesNotExist:
            raise graphene.GraphQLError("Agent does not exist.")


class CommandAuthorizeInput(graphene.InputObjectType):
    message_id = graphene.UUID(required=True)


class AuthorizeCommandMutation(graphene.Mutation):
    class Arguments:
        input = CommandAuthorizeInput(required=True)

    task_log_message = graphene.Field(TaskLogMessageType)
    errors = graphene.Field(graphene.List(graphene.String))

    @staticmethod
    @handle_exceptions
    def mutate(root, info, input):
        # save to persistent storage
        responding_to = TaskLogMessage.objects.get(pk=input.message_id)
        message = TaskLogMessage.objects.create(
            task_id=responding_to.task_id,
            parent_id=responding_to.parent_id,
            role="USER",
            content=UserFeedback(
                type="AUTHORIZE",
                message_id=str(input.message_id),
            ),
        )

        # TODO: here or in a chain node?
        authorized_msg = TaskLogMessage.objects.get(pk=input.message_id)
        [reference_field, reference_value] = list(
            authorized_msg.content["storage"].items()
        )[0]
        inputs = dict(
            user_input=f"execute {reference_field}={reference_value}",
            **authorized_msg.content["storage"],
        )

        # resume task loop
        # This does NOT check if the loop is already running
        # the agent_runner task is responsible for blocking duplicate runners
        logger.info(
            f"Requesting agent loop resume task_id={message.task_id} message_id={message.pk}"
        )
        task = responding_to.task
        start_agent_loop.delay(
            task_id=str(responding_to.task_id),
            chain_id=str(task.chain_id),
            inputs=inputs,
        )

        return TaskLogMessageResponse(task_log_message=message)


class TaskLogMessageResponse(graphene.ObjectType):
    task_log_message = graphene.Field(TaskLogMessage)
    errors = graphene.List(graphene.String)

    def resolve_task_log(root, info):
        return root.task_log


class ChatInput(graphene.InputObjectType):
    chat_id = graphene.UUID(required=True)
    text = graphene.String(required=True)


def get_artifacts(user_input):
    """Find all references to artifacts in user input."""
    # Pattern to find all instances of text enclosed in curly braces.
    pattern = r"\{(.*?)\}"

    # re.findall returns all non-overlapping matches of pattern in string, as a list of strings.
    # The string is scanned left-to-right, and matches are returned in the order found.
    matches = re.findall(pattern, user_input)

    # Return the list of matches.
    return matches


class ChatInputMutation(graphene.Mutation):
    class Arguments:
        input = ChatInput(required=True)

    task_log_message = graphene.Field(TaskLogMessageType)
    errors = graphene.Field(graphene.List(graphene.String))

    @staticmethod
    @handle_exceptions
    def mutate(root, info, input):
        chat = Chat.objects.get(pk=input.chat_id)

        # save to persistent storage
        message = TaskLogMessage.objects.create(
            task_id=chat.task_id,
            role="USER",
            content=UserFeedback(
                type="FEEDBACK",
                feedback=input.text,
            ),
        )

        # determine if user targeted a specific agent in the chat
        # if so, forward the message to that agent
        # otherwise, forward the message to the lead agent
        agent = chat.lead
        task_id = chat.task_id
        user_input = input.text.strip().lower()
        if user_input.startswith("@"):
            # Find the first space or the end of the string
            space_index = user_input.find(" ")
            if space_index == -1:
                space_index = len(user_input)

            # Extract the agent name and find the agent
            agent_alias = user_input[1:space_index]

            agent = Agent.objects.filter(
                Q(leading_chats=chat, alias=agent_alias)
                | Q(chats__id=chat.id, alias=agent_alias)
            ).get()

            # delegate the task to the agent and run in this thread
            subtask = chat.task.delegate_to_agent(agent)
            task_id = subtask.id

        # resume task loop
        logger.info(
            f"Requesting agent loop resume chat_id={chat.id} task_id={message.task_id} user_input={message.pk}"
        )

        inputs = {
            "user_input": input.text,
            "chat_id": str(chat.id),
            "artifact_keys": get_artifacts(user_input) or [],
        }

        # Start agent loop. This does NOT check if the loop is already running
        # the agent_runner task is responsible for blocking duplicate runners
        start_agent_loop.delay(str(task_id), str(agent.chain.id), inputs=inputs)

        return TaskLogMessageResponse(task_log_message=message)


class Mutation(graphene.ObjectType):
    """
    Aggregation of chat mutations
    """

    sendInput = ChatInputMutation.Field()
    authorize_command = AuthorizeCommandMutation.Field()

    # chat management
    create_chat = CreateChatMutation.Field()
    remove_agent = RemoveAgentMutation.Field()
    add_agent = AddAgentMutation.Field()
