import logging

import graphene
import channels_graphql_ws

from ix.chat.models import Chat
from ix.schema.types.agents import AgentType
from ix.schema.types.messages import TaskLogMessageType
from ix.task_log.models import TaskLogMessage, Task

logger = logging.getLogger(__name__)


class ChatMessageSubscription(channels_graphql_ws.Subscription):
    """GraphQL subscription to TaskLogMessage instances."""

    # Subscription payload - FKs aren't working over websockets
    # so add related objects manually
    task_log_message = graphene.Field(TaskLogMessageType)
    agent = graphene.Field(AgentType)
    parent_id = graphene.UUID()

    class Arguments:
        """Subscription arguments."""

        chatId = graphene.String()

    @staticmethod
    async def subscribe(root, info, chatId):
        """Called when user subscribes."""
        chat = await Chat.objects.filter(id=chatId).select_related("task").aget()
        logger.debug(f"client subscribing to chatId: {chatId} chat.task.id: {chat.task_id}")
        return ["chat_1"]
        #return [f"task_id_{chat.task_id}"]

    @staticmethod
    async def publish(payload, info, chatId):
        """Called to notify the client."""
        msg = payload.get("instance")
        chat = await Chat.objects.aget(id=chatId)
        logger.debug(f"publishing chatId={chatId}, msg.task.id={msg.task_id} msg.content={msg.content}")

        task = await Task.objects.aget(pk=msg.task_id)
        parent_id = task.parent_id
        task_id = parent_id if parent_id else msg.task_id

        if task_id == chat.task_id:
            # django query for related objects needed to be done async
            msg_with_related = (
                await TaskLogMessage.objects.filter(id=msg.id)
                .select_related("agent", "parent")
                .aget()
            )

            return ChatMessageSubscription(
                task_log_message=msg_with_related,
                agent=msg_with_related.agent,
                parent_id=msg_with_related.parent_id,
            )
        else:
            logger.error("SKIPPED!")
            return None

    @classmethod
    def new_task_log_message(cls, sender, **kwargs):
        """Called when new task log message instance is saved."""
        instance = kwargs["instance"]

        parent_id = instance.task.parent_id
        task_id = parent_id if parent_id else instance.task_id
        logger.info(f"new_task_log_message={instance} task_id={task_id} parent_id={parent_id} instance.task_id={instance.task_id}")
        cls.broadcast(
            group="chat_1",
            #group=f"task_id_{task_id}",  # assuming each task is associated with one chat
            payload={"instance": instance},
        )


class Subscription(graphene.ObjectType):
    """Root GraphQL subscription."""

    chatMessageSubscription = ChatMessageSubscription.Field()
