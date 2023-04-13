import logging
import graphene
from graphene_django import DjangoObjectType

from ix.task_log.models import TaskLogMessage


logger = logging.getLogger(__name__)


class MessageContentType(graphene.ObjectType):
    type = graphene.String(required=True)


class ThoughtsType(graphene.ObjectType):
    text = graphene.String(required=True)
    reasoning = graphene.String(required=True)
    plan = graphene.List(graphene.String, required=True)
    criticism = graphene.String(required=True)
    speak = graphene.String()


class CommandType(graphene.ObjectType):
    name = graphene.String(required=True)
    args = graphene.JSONString(required=False)


class AssistantContentType(MessageContentType):
    thoughts = graphene.Field(ThoughtsType, required=True)
    command = graphene.Field(CommandType, required=True)


class FeedbackContentType(MessageContentType):
    authorized = graphene.Int()
    feedback = graphene.String()


class SystemContentType(MessageContentType):
    message = graphene.String(required=True)


class FeedbackRequestContentType(MessageContentType):
    message = graphene.String(required=True)


class MessageContentType(graphene.Union):
    class Meta:
        types = (
            AssistantContentType,
            FeedbackRequestContentType,
            FeedbackContentType,
            SystemContentType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        message_type = instance.get("type")
        if message_type == "ASSISTANT":
            return AssistantContentType
        elif message_type == "FEEDBACK_REQUEST":
            return FeedbackRequestContentType
        elif message_type == "FEEDBACK":
            return FeedbackContentType
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
