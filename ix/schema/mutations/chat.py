import logging
import graphene

from ix.schema.types.messages import TaskLogMessageType
from ix.schema.utils import handle_exceptions
from ix.task_log.models import TaskLogMessage, UserFeedback
from ix.task_log.tasks.agent_runner import (
    start_agent_loop,
)


logger = logging.getLogger(__name__)


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
            role="USER",
            content=UserFeedback(
                type="AUTHORIZE",
                message_id=str(input.message_id),
            ),
        )

        # resume task loop
        # This does NOT check if the loop is already running
        # the agent_runner task is responsible for blocking duplicate runners
        logger.info(
            f"Requesting agent loop resume task_id={message.task_id} message_id={message.pk}"
        )
        start_agent_loop.delay(str(responding_to.task_id), message_id=str(message.id))

        return TaskLogMessageResponse(task_log_message=message)


class TaskLogMessageResponse(graphene.ObjectType):
    task_log_message = graphene.Field(TaskLogMessage)
    errors = graphene.List(graphene.String)

    def resolve_task_log(root, info):
        return root.task_log


class TaskFeedbackInput(graphene.InputObjectType):
    task_id = graphene.UUID(required=True)
    feedback = graphene.String(required=True)


class TaskFeedbackMutation(graphene.Mutation):
    class Arguments:
        input = TaskFeedbackInput(required=True)

    task_log_message = graphene.Field(TaskLogMessageType)
    errors = graphene.Field(graphene.List(graphene.String))

    @staticmethod
    @handle_exceptions
    def mutate(root, info, input):
        # save to persistent storage
        message = TaskLogMessage.objects.create(
            task_id=input.task_id,
            role="USER",
            content=UserFeedback(
                type="FEEDBACK",
                feedback=input.feedback,
            ),
        )

        # resume task loop
        logger.info(
            f"Requesting agent loop resume task_id={message.task_id} message_id={message.pk}"
        )

        # Start agent loop. This does NOT check if the loop is already running
        # the agent_runner task is responsible for blocking duplicate runners
        start_agent_loop.delay(str(input.task_id), input_id=message.id)

        return TaskLogMessageResponse(task_log_message=message)


class Mutation(graphene.ObjectType):
    """
    Aggregation of chat mutations
    """

    send_feedback = TaskFeedbackMutation.Field()
    authorize_command = AuthorizeCommandMutation.Field()
