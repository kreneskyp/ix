import logging
import time
import traceback

from functools import cached_property
from typing import TypedDict, Optional, Any, Dict

from langchain.chains.base import Chain

from ix.agents.callback_manager import IxCallbackManager
from ix.agents.exceptions import (
    AgentQuestion,
    AuthRequired,
)
from ix.chains.models import Chain as ChainModel
from ix.task_log.models import Task, TaskLogMessage
from ix.utils.importlib import import_class


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
    # initial command when first starting
    INITIAL_INPUT = None

    # the default prompt to use if not given FEEDBACK
    NEXT_COMMAND = None

    # indicates if the agent should be allowed to run autonomously
    ALLOWS_AUTONOMOUS = True

    def __init__(
        self,
        task_id: int,
        chain_id: str,
    ):
        logger.info(f"AgentProcess initializing task_id={task_id}")

        # initial state
        self.task_id = task_id
        self.chain_id = chain_id
        self.autonomous = 0

    @cached_property
    def task(self):
        return Task.objects.get(pk=self.task_id)

    @cached_property
    def agent(self):
        return self.task.agent

    @cached_property
    def chain(self):
        return ChainModel.objects.get(pk=self.chain_id)

    @classmethod
    def from_task(cls, task: Task) -> "AgentProcess":
        """
        Create an agent process from a task object. This will create an instance of the
        agent class defined in the task and initialize it with the task id.
        """
        agent_class = import_class(task.agent.agent_class_path)
        assert issubclass(agent_class, cls)
        return agent_class(task_id=task.id)

    def start(self, inputs: Optional[Dict[str, Any]] = None, n: int = 0) -> bool:
        """
        start agent loop and process `n` authorized ticks.
        """
        logger.info(f"starting process loop task_id={self.task_id} input_id={inputs}")
        authorized_for = n

        # pass to main loop
        exit_value = self.loop(n=authorized_for, tick_input=inputs)
        logger.info(
            f"exiting process loop task_id={self.task_id} exit_value={exit_value}"
        )
        return exit_value

    def loop(self, n=1, tick_input: Optional[Dict[str, Any]] = NEXT_COMMAND) -> bool:
        """
        main loop for agent process
        :param n: number of ticks user has authorized
        :param tick_input: initial input for first tick
        :return:
        """
        loop_input = tick_input
        for i in range(n + 1):
            execute = self.autonomous or i < n
            if not self.tick(execute=execute, user_input=loop_input):
                logger.info("exiting loop, tick=False")
                return False
            loop_input = self.NEXT_COMMAND
        return True

    def tick(
        self, user_input: Optional[Dict[str, Any]] = None, execute: bool = False
    ) -> bool:
        """
        "tick" the agent loop letting it chat and run commands. The chat interaction
        including feedback requests, authorization requests, command results, and
        errors are logged.

        :param user_input: the next command to run or NEXT_COMMAND
        :param execute: execute the command or just chat
        :return: True to continue, False to exit
        """
        logger.debug(
            "=== TICK =================================================================="
        )
        logger.info(f"ticking task_id={self.task_id} user_input={user_input}")

        think_msg = TaskLogMessage.objects.create(
            task_id=self.task_id,
            role="system",
            content={"type": "THINK", "input": user_input, "agent": self.agent.alias},
        )
        try:
            response = self.chat_with_ai(think_msg, user_input)
            logger.debug(
                f"Response from model, task_id={self.task_id} response={response}"
            )

        except AgentQuestion as question:
            # Agent returned a question that requires a response from the user.
            # Abort normal execution and request INPUT from the user.
            TaskLogMessage.objects.create(
                task_id=self.task_id,
                parent_id=think_msg.id,
                role="assistant",
                content=dict(type="FEEDBACK_REQUEST", question=question.message),
            )
            return False

        except AuthRequired as e:
            self.request_user_auth(think_msg, e.message)
            return False

        except Exception as e:
            # catch all to log all other messages
            self.log_exception(exception=e, think_msg=think_msg)
            return True
        return True

    def log_exception(
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
        failure_msg = TaskLogMessage.objects.create(
            task_id=self.task_id,
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

    def chat_with_ai(
        self, think_msg: TaskLogMessage, user_input: Dict[str, Any]
    ) -> TaskLogMessage:
        callback_manager = IxCallbackManager(self.task)
        callback_manager.think_msg = think_msg
        chain = self.chain.load_chain(callback_manager)

        logger.info(
            f"Sending request to chain={self.task.agent.chain.name} prompt={user_input}"
        )

        start = time.time()
        try:
            response = chain.run(**user_input)
        except:  # noqa: E722
            raise
        finally:
            end = time.time()
            TaskLogMessage.objects.create(
                task_id=self.task_id,
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

    def request_user_auth(self, think_msg: TaskLogMessage, message: TaskLogMessage):
        """
        Request user input to authorize command.
        """
        logger.info(
            f"requesting user authorization task_id={self.task_id} message_id={message.id}"
        )
        TaskLogMessage.objects.create(
            task_id=self.task_id,
            parent=think_msg,
            role="assistant",
            content={
                "type": "AUTH_REQUEST",
                "message_id": str(message.id),
            },
        )
