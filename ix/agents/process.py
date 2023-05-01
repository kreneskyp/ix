import logging
import time
import uuid

from functools import cached_property
from typing import TypedDict, Optional, Any, Dict, Tuple

from langchain.chains.base import Chain

from ix.agents.callback_manager import IxCallbackManager
from ix.agents.exceptions import (
    AgentQuestion,
    AuthRequired,
)
from ix.memory.plugin import VectorMemory
from ix.server import settings
from ix.task_log.models import Task, TaskLogMessage
from ix.utils.importlib import import_class
from ix.utils.types import ClassPath


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

    # Messages useful for humans and debugging, but aren't included in the prompt context
    EXCLUDED_MSG_TYPES = {
        "AUTH_REQUEST",
        "AUTHORIZE",
        "AUTONOMOUS",
        "FEEDBACK_REQUEST",
        "THOUGHT",
        "SYSTEM",
    }

    def __init__(
        self,
        task_id: int,
        memory_class: ClassPath = DEFAULT_MEMORY,
    ):
        logger.info(f"AgentProcess initializing task_id={task_id}")

        # agent config
        self.memory_class = memory_class

        # initial state
        self.task_id = task_id
        self.history = []
        self.last_message = None
        self.memory = None
        self.autonomous = 0

        # task int
        self.update_message_history()
        self.initialize_memory()
        logger.info("AgentProcess initialized")

    @cached_property
    def task(self):
        return Task.objects.get(pk=self.task_id)

    @cached_property
    def agent(self):
        return self.task.agent

    @classmethod
    def from_task(cls, task: Task) -> "AgentProcess":
        """
        Create an agent process from a task object. This will create an instance of the
        agent class defined in the task and initialize it with the task id.
        """
        agent_class = import_class(task.agent.agent_class_path)
        assert issubclass(agent_class, cls)
        return agent_class(task_id=task.id)

    def query_message_history(self, since=None):
        """Fetch message history from persistent store for context relevant messages"""

        # base query, selects messages relevant for chat context
        query = TaskLogMessage.objects.filter(task_id=self.task_id).order_by(
            "created_at"
        )

        # filter to only new messages
        if since:
            query = query.filter(created_at__gt=since)

        return query

    def update_message_history(self):
        """
        Update message history with the most recent messages since the last update.
        Initial startup will load all history into memory. Subsequent updates will
        only load new messages.
        """

        last_message_at = self.last_message.created_at if self.last_message else None
        logger.debug(
            f"AgentProcess updating message history, last_message_at={last_message_at}"
        )

        # fetch unseen messages and save the last timestamp for the next iteration
        messages = list(self.query_message_history(last_message_at))
        if messages:
            self.last_message = messages[-1]
        logger.debug(
            f"AgentProcess fetched n={len(messages)} messages from persistence"
        )

        # process AUTONOMOUS messages if supported by the agent
        # toggle autonomous mode based on latest AUTONOMOUS message
        if self.ALLOWS_AUTONOMOUS:
            for message in reversed(messages):
                if message.content["type"] == "AUTONOMOUS":
                    autonomous = message.content["enabled"]
                    if autonomous != self.autonomous:
                        self.autonomous = autonomous
                        logger.info(
                            f"AgentProcess toggled autonomous mode to {autonomous}"
                        )
                    break

        # format all message instance for use in the prompt
        formatted_messages = [
            message.as_message()
            for message in messages
            if message.content["type"] not in self.EXCLUDED_MSG_TYPES
        ]
        self.add_history(*formatted_messages)

        logger.info(
            f"AgentProcess loaded n={len(messages)} chat messages from persistence"
        )

    def initialize_memory(self):
        """Load and initialize configured memory class"""
        logger.debug("initializing memory_class={self.memory_class}")
        memory_class = import_class(self.memory_class)
        assert issubclass(memory_class, VectorMemory)
        self.memory = memory_class("ix-agent")
        self.memory.clear()

    def start(self, input_id: Optional[uuid.UUID] = None, n: int = 0) -> bool:
        """
        start agent loop and process `n` authorized ticks.
        """
        logger.info(f"starting process loop task_id={self.task_id} input_id={input_id}")
        tick_input = None
        authorized_for = n
        try:
            self.last_message = TaskLogMessage.objects.filter(
                task_id=self.task_id
            ).latest("created_at")
        except TaskLogMessage.DoesNotExist:
            self.last_message = None

        logger.debug(f"task_id={self.task_id} last message={self.last_message}")

        if not self.last_message:
            logger.info(f"first tick for task_id={self.task_id}")
            tick_input = {"user_input": self.INITIAL_INPUT}
            # TODO load initial auth from either message stream or task
        elif input_id is not None:
            message = TaskLogMessage.objects.get(id=input_id)
            tick_input = {"user_input": message.content["feedback"]}
        elif self.last_message.content["type"] == "FEEDBACK":
            tick_input = {"user_input": self.last_message.content["feedback"]}
        elif self.last_message.content["type"] == "AUTHORIZE":
            logger.info(f"resuming with user authorization for task_id={self.task_id}")
            # auth/feedback resume, run command that was authorized
            # by default only a single command is authorized.
            authorized_for = self.last_message.content.get("n", 1) - 1
            authorized_msg = TaskLogMessage.objects.get(
                pk=self.last_message.content["message_id"]
            )
            self.msg_execute(authorized_msg)
        elif self.last_message.content["type"] in ["AUTH_REQUEST", "FEEDBACK_REQUEST"]:
            # if last message is an unfulfilled feedback request then exit
            logger.info(
                f"Exiting, missing response to type={self.last_message.content['type']}"
            )
            return True

        # pass to main loop
        exit_value = self.loop(n=authorized_for, tick_input=tick_input)
        logger.info(
            f"exiting process loop task_id={self.task_id} exit_value={exit_value}"
        )
        return exit_value

    def loop(self, n=1, tick_input: str = NEXT_COMMAND) -> bool:
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

    def tick(self, user_input: Optional[str] = None, execute: bool = False) -> bool:
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
        self.update_message_history()
        logger.info(f"ticking task_id={self.task_id}")

        think_msg = None
        try:
            think_msg, response = self.chat_with_ai(user_input)
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
            raise
            return True

    def log_exception(
        self,
        exception: Exception,
        think_msg: TaskLogMessage = None,
    ):
        """Collection point for errors while ticking the loop"""
        assert isinstance(exception, Exception), exception
        error_type = type(exception).__name__
        think_msg_id = think_msg.id if think_msg else None
        failure_msg = TaskLogMessage.objects.create(
            task_id=self.task_id,
            parent_id=think_msg_id,
            role="system",
            content={
                "type": "EXECUTE_ERROR",
                "error_type": error_type,
                "text": str(exception),
            },
        )
        logger.error(
            f"@@@@ EXECUTE ERROR logged as id={failure_msg.id} message_id={think_msg_id} error_type={error_type}"
        )
        logger.error(f"@@@@ EXECUTE ERROR {failure_msg.content['text']}")

    def construct_chain(self) -> Chain:
        callback_manager = IxCallbackManager(self.task)
        # [
        #     OpenAICallbackHandler(),
        #     IxCallbackHandler(task=self.task)
        # ]
        from ix.chains.models import Chain as ChainModel

        # TODO: load from agent
        chain = ChainModel.objects.get()
        return chain.load_chain(callback_manager)

    def chat_with_ai(self, user_input) -> Tuple[TaskLogMessage, str]:
        agent = self.task.agent
        chain = self.construct_chain()
        logger.info(f"Sending request to model={agent.model} prompt={user_input}")

        think_msg = TaskLogMessage.objects.create(
            task_id=self.task_id,
            role="system",
            content={
                "type": "THINK",
                "input": user_input,
            },
        )
        start = time.time()
        response = chain.run(**user_input)
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
        return think_msg, response

    def add_history(self, *history_messages: Dict[str, Any]):
        logger.debug(f"adding history history_messages={history_messages}")
        self.history.extend(history_messages)

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
