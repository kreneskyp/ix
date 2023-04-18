import logging
import graphene
from graphene_django import DjangoObjectType

from ix.task_log.models import TaskLogMessage


logger = logging.getLogger(__name__)


class MessageContentType(graphene.ObjectType):
    """
    Base type for all messages.

    This class exists largely to unify the `type` property. It's not great that this lives
    here rather than on the parent `MessageContentType` that unions all message types into
    a single type. `MessageContentType` didn't have access to the parent class
    `TaskLogMessageType`
    """

    type = graphene.String(required=True)


class ThoughtsType(graphene.ObjectType):
    """Assistant thoughts"""

    text = graphene.String(required=True)
    reasoning = graphene.String(required=True)
    plan = graphene.List(graphene.String, required=True)
    criticism = graphene.String(required=True)
    speak = graphene.String()


class CommandType(graphene.ObjectType):
    """Assistant command"""

    name = graphene.String(required=True)
    args = graphene.JSONString(required=False)


class AssistantContentType(MessageContentType):
    """
    Assistant reply with thoughts and command. Sent in response to prompt
    requesting the next command
    """

    thoughts = graphene.Field(ThoughtsType, required=True)
    command = graphene.Field(CommandType, required=True)


class FeedbackContentType(MessageContentType):
    """User feedback sent to agent"""

    feedback = graphene.String(required=True)


class AuthorizeContentType(MessageContentType):
    """User granting permission for agent to run a command"""

    message_id = graphene.ID(required=True)


class SystemContentType(MessageContentType):
    """All system messages"""

    message = graphene.String(required=True)


class ExecutedContentType(MessageContentType):
    """Sent when the agent executes a command"""

    message_id = graphene.ID(required=True)
    output = graphene.String(required=True)


class ExecuteErrorContentType(MessageContentType):
    """Sent when an error occurs while executing a command"""

    related_message_id = graphene.ID(required=False)
    error_type = graphene.String(required=True)
    text = graphene.String(required=True)


class FeedbackRequestContentType(MessageContentType):
    """Sent when the agent requests user feedback on a command or output"""

    question = graphene.String(required=True)


class AuthRequestContentType(MessageContentType):
    """Sent when the agent requires permission to run a command"""

    message_id = graphene.ID(required=True)


class AutonomousModeContentType(MessageContentType):
    """
    Instructs the agent to enable/disable autonomous mode. Mode
    change takes effect starting with the next agent process loop tick.
    """

    enabled = graphene.Int(required=True)


class MessageContentType(graphene.Union):
    """
    Union of all message types sent to the task log API.
    """

    class Meta:
        types = (
            AssistantContentType,
            AutonomousModeContentType,
            AuthorizeContentType,
            AuthRequestContentType,
            ExecutedContentType,
            ExecuteErrorContentType,
            FeedbackRequestContentType,
            FeedbackContentType,
            SystemContentType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        message_type = instance.get("type")
        if message_type == "ASSISTANT":
            return AssistantContentType
        elif message_type == "AUTH_REQUEST":
            return AuthRequestContentType
        elif message_type == "EXECUTED":
            return ExecutedContentType
        elif message_type == "EXECUTE_ERROR":
            return ExecuteErrorContentType
        elif message_type == "FEEDBACK_REQUEST":
            return FeedbackRequestContentType
        elif message_type == "FEEDBACK":
            return FeedbackContentType
        elif message_type == "AUTHORIZE":
            return AuthorizeContentType
        elif message_type == "AUTONOMOUS":
            return AutonomousModeContentType
        elif message_type == "SYSTEM":
            return SystemContentType
        else:
            # Raise an exception if the message_type is not recognized.
            raise Exception("Unknown message_type for MessageContentType.")


class TaskLogMessageType(DjangoObjectType):
    class Meta:
        model = TaskLogMessage
        fields = "__all__"

    content = MessageContentType()
