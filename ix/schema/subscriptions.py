import logging

import graphene
import channels_graphql_ws

from ix.chat.models import Chat
from ix.schema.types.agents import AgentType
from ix.schema.types.messages import TaskLogMessageType

logger = logging.getLogger(__name__)


class ChatMessageSubscription(channels_graphql_ws.Subscription):
    """GraphQL subscription to TaskLogMessage instances."""

    # Subscription payload - FKs aren't working over websockets
    # so add related objects manually
    task_log_message = graphene.Field(TaskLogMessageType)
    agent = graphene.Field(AgentType)
    parent_id = graphene.UUID()

    class Arguments:
        chatId = graphene.String()

    @staticmethod
    async def subscribe(root, info, chatId):
        """Called when client subscribes."""
        logger.debug(f"client subscribing to chatId: {chatId}")
        chat = await Chat.objects.aget(id=chatId)
        task_id = chat.task_id
        return [f"task_id_{task_id}"]

    @staticmethod
    async def publish(payload, info, chatId):
        """Called to notify subscribed clients."""
        msg = payload.get("instance")
        agent = payload.get("agent")
        return ChatMessageSubscription(
            task_log_message=msg, parent_id=msg.parent_id, agent=agent
        )

    @classmethod
    def new_task_log_message(cls, sender, **kwargs):
        """
        Called when new task log message instance is saved. Messages are
        Broadcast to all clients subscribed to the chat's task_id.
        Subtasks are broadcast to the parent task's task_id.
        """
        instance = kwargs["instance"]

        parent_id = instance.task.parent_id
        task_id = parent_id if parent_id else instance.task_id
        cls.broadcast(
            group=f"task_id_{task_id}",
            payload={"instance": instance, "agent": instance.task.agent},
        )


class Subscription(graphene.ObjectType):
    """Root GraphQL subscription."""

    chatMessageSubscription = ChatMessageSubscription.Field()
