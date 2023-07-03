import logging
import time
import traceback

from typing import TypedDict, Optional, Any, Dict

from asgiref.sync import sync_to_async

from ix.agents.callback_manager import IxCallbackManager
from ix.agents.exceptions import (
    AgentQuestion,
    AuthRequired,
)
from ix.agents.models import Agent
from ix.chains.models import Chain as ChainModel
from ix.task_log.models import Task, TaskLogMessage


# config defaults
DEFAULT_COMMANDS = [
    "ix.commands.google",
    "ix.commands.filesystem",
    "ix.commands.execute",
]
DEFAULT_MEMORY = "ix.memory.redis.RedisVectorMemory"
DEFAULT_MEMORY_OPTIONS = {"host": "redis"}


# logging
logger = logging.getLogger(__name__)


class UserInput(TypedDict):
    authorized_ticks: int
    feedback: Optional[str]


class ChatMessage(TypedDict):
    role: str
    content: str


class AgentProcess:
    def __init__(
        self,
        task: Task,
        agent: Agent,
        chain: ChainModel,
    ):
        self.chain = chain
        self.task = task
        self.agent = agent

    async def start(self, inputs: Optional[Dict[str, Any]] = None) -> bool:
        """
        start agent loop and process `n` authorized ticks.
        """
        logger.info(f"starting process loop task_id={self.task.id} input_id={inputs}")

        think_msg = await TaskLogMessage.objects.acreate(
            task_id=self.task.id,
            role="system",
            content={"type": "THINK", "input": inputs, "agent": self.agent.alias},
        )
        try:
            response = await self.chat_with_ai(think_msg, inputs)
            logger.debug(
                f"Response from model, task_id={self.task.id} response={response}"
            )

        except AgentQuestion as question:
            # Agent returned a question that requires a response from the user.
            # Abort normal execution and request INPUT from the user.
            return False
            await TaskLogMessage.objects.acreate(
                task_id=self.task.id,
                parent_id=think_msg.id,
                role="assistant",
                content=dict(type="FEEDBACK_REQUEST", question=question.message),
            )
            return False

        except AuthRequired as e:
            await self.request_user_auth(think_msg, e.message)
            return False

        except Exception as e:
            # catch all to log all other messages
            await self.log_exception(exception=e, think_msg=think_msg)
            return True
        return True

    async def log_exception(
        self,
        exception: Exception,
        think_msg: TaskLogMessage = None,
    ):
        """Collection point for errors while ticking the loop"""
        assert isinstance(exception, Exception), exception
        traceback_list = traceback.format_exception(
            type(exception), exception, exception.__traceback__
        )
        traceback_string = "".join(traceback_list)
        error_type = type(exception).__name__
        think_msg_id = think_msg.id if think_msg else None
        failure_msg = await TaskLogMessage.objects.acreate(
            task_id=self.task.id,
            parent_id=think_msg_id,
            role="assistant",
            content={
                "type": "EXECUTE_ERROR",
                "error_type": error_type,
                "text": str(exception),
                "details": traceback_string,
            },
        )
        logger.error(
            f"@@@@ EXECUTE ERROR logged as id={failure_msg.id} message_id={think_msg_id} error_type={error_type}"
        )
        logger.error(f"@@@@ EXECUTE ERROR {failure_msg.content['text']}")
        raise

    async def chat_with_ai(
        self, think_msg: TaskLogMessage, user_input: Dict[str, Any]
    ) -> TaskLogMessage:
        callback_manager = IxCallbackManager(self.task, self.agent)
        callback_manager.think_msg = think_msg

        # TODO: chain loading needs to be made async
        chain = await sync_to_async(self.chain.load_chain)(callback_manager)

        logger.info(f"Sending request to chain={self.chain.name} prompt={user_input}")

        start = time.time()
        try:
            # Hax: copy user_input to input to support agents.
            response = await chain.arun(input=user_input["user_input"], **user_input)
        except:  # noqa: E722
            raise
        finally:
            end = time.time()
            await TaskLogMessage.objects.acreate(
                task_id=self.task.id,
                role="system",
                parent_id=think_msg.id,
                content={
                    "type": "THOUGHT",
                    # TODO: add usage in somewhere else, it's not provided by langchain
                    # "usage": response["usage"],
                    "runtime": end - start,
                },
            )
        return response

    async def request_user_auth(
        self, think_msg: TaskLogMessage, message: TaskLogMessage
    ):
        """
        Request user input to authorize command.
        """
        logger.info(
            f"requesting user authorization task_id={self.task.id} message_id={message.id}"
        )
        await TaskLogMessage.objects.acreate(
            task_id=self.task.id,
            parent=think_msg,
            role="assistant",
            content={
                "type": "AUTH_REQUEST",
                "message_id": str(message.id),
            },
        )
