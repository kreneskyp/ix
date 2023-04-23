import logging
import json
import time

import openai
from functools import cached_property
from typing import TypedDict, Optional, List, Any, Dict, Tuple

from ix.agents.prompt_builder import PromptBuilder
from ix.agents.prompts import COMMAND_FORMAT
from ix.memory.plugin import VectorMemory
from ix.task_log.models import Task, TaskLogMessage
from ix.commands.registry import CommandRegistry
from ix.utils.importlib import import_class
from ix.utils.types import ClassPath


class ResponseParseError(Exception):
    """Exception thrown when response parsing fails"""


class MissingCommandMarkers(ResponseParseError):
    """Exception thrown when command markers are missing from response"""


class UnknownCommand(ResponseParseError):
    """Exception thrown when command is not recognized"""


class MissingCommand(ResponseParseError):
    """Exception thrown when command is not present in parsed response"""


class AgentQuestion(Exception):
    """Exception thrown when the agent needs to ask a question"""

    def __init__(self, message: str):
        self.message = message


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
    INITIAL_INPUT = (
        "Determine which next command to use, and respond in the expected format"
    )
    # NEXT_COMMAND = "GENERATE NEXT COMMAND JSON"
    NEXT_COMMAND = INITIAL_INPUT
    EXCLUDED_MSG_TYPES = {
        "AUTH_REQUEST",
        "AUTHORIZE",
        "AUTONOMOUS",
        "FEEDBACK_REQUEST",
        "THOUGHT",
        "SYSTEM",
    }

    command_registry: CommandRegistry

    def __init__(
        self,
        task_id: int,
        memory_class: ClassPath = DEFAULT_MEMORY,
        command_modules: List[ClassPath] = DEFAULT_COMMANDS,
    ):
        logger.info(f"AgentProcess initializing task_id={task_id}")

        # agent config
        self.memory_class = memory_class
        self.command_modules = command_modules

        # initial state
        self.task_id = task_id
        self.history = []
        self.last_message_at = None
        self.memory = None
        self.autonomous = 0

        # agent init
        self.init_commands()

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
        logger.debug(
            f"AgentProcess updating message history, last_message_at={self.last_message_at}"
        )

        # fetch unseen messages and save the last timestamp for the next iteration
        messages = list(self.query_message_history(self.last_message_at))
        if messages:
            self.last_message_at = messages[-1].created_at
        logger.debug(
            f"AgentProcess fetched n={len(messages)} messages from persistence"
        )

        # toggle autonomous mode based on latest AUTONOMOUS message
        for message in reversed(messages):
            if message.content["type"] == "AUTONOMOUS":
                autonomous = message.content["enabled"]
                if autonomous != self.autonomous:
                    self.autonomous = autonomous
                    logger.info(f"AgentProcess toggled autonomous mode to {autonomous}")
                break

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

    def init_commands(self):
        """Load commands for this agent"""
        logger.debug("initializing commands")
        self.command_registry = CommandRegistry()
        for class_path in self.command_modules:
            self.command_registry.import_commands(class_path)

        logger.info("intialized command registry")

    def start(self, n: int = 0) -> bool:
        """
        start agent loop and process `n` authorized ticks.
        """
        logger.info(f"starting process loop task_id={self.task_id}")
        tick_input = self.NEXT_COMMAND
        authorized_for = n
        try:
            last_message = TaskLogMessage.objects.filter(task_id=self.task_id).latest(
                "created_at"
            )
        except TaskLogMessage.DoesNotExist:
            last_message = None

        if not last_message:
            logger.info(f"first tick for task_id={self.task_id}")
            tick_input = self.INITIAL_INPUT
            # TODO load initial auth from either message stream or task
        elif last_message.content["type"] == "AUTHORIZE":
            logger.info(f"resuming with user authorization for task_id={self.task_id}")
            # auth/feedback resume, run command that was authorized
            # by default only a single command is authorized.
            authorized_for = last_message.content.get("n", 1) - 1
            authorized_msg = TaskLogMessage.objects.get(
                pk=last_message.content["message_id"]
            )
            self.msg_execute(authorized_msg)
        elif last_message.content["type"] in ["AUTH_REQUEST", "FEEDBACK_REQUEST"]:
            # if last message is an unfulfilled feedback request then exit
            logger.info(
                f"Exiting, missing response to type={last_message.content['type']}"
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
        for i in range(n + 1):
            execute = self.autonomous or i < n
            if not self.tick(execute=execute):
                logger.info("exiting loop, tick=False")
                return False
        return True

    def tick(self, user_input: str = NEXT_COMMAND, execute: bool = False) -> bool:
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
        think_msg, response = self.chat_with_ai(user_input)
        logger.debug(f"Response from model, task_id={self.task_id} response={response}")

        try:
            parsed_response = self.parse_response(think_msg, response)
        except ResponseParseError as e:
            # log parse error and return True to retry
            # if the loop has more ticks remaining
            self.log_exception(e, think_msg)
            return True
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

        # log command to persistent storage
        log_message = TaskLogMessage.objects.create(
            task_id=self.task_id,
            parent_id=think_msg.id,
            role="assistant",
            content=dict(type="COMMAND", **data),
        )

        # validate command and then execute or seek feedback
        if (
            "command" not in data
            or "name" not in data["command"]
            or "args" not in data["command"]
            or not data["command"]
        ):
            TaskLogMessage.objects.create(
                task_id=self.task_id,
                parent_id=think_msg.id,
                role="system",
                content={
                    "type": "EXECUTE_ERROR",
                    "message_id": str(log_message.id),
                    "error_type": "missing command",
                    "text": "respond in the expected format",
                },
            )
        elif data["command"]["name"] not in self.command_registry.commands:
            TaskLogMessage.objects.create(
                task_id=self.task_id,
                parent_id=think_msg.id,
                role="system",
                content={
                    "type": "EXECUTE_ERROR",
                    "message_id": str(log_message.id),
                    "error_type": "unknown command",
                    "text": f'{data["command"]["name"]} is not available',
                },
            )
        else:
            command = self.command_registry.get(data["command"]["name"])
            logger.info(f"model returned task_id={self.task_id} command={command.name}")
            if execute:
                return self.msg_execute(log_message)
            else:
                logger.info(f"requesting user authorization task_id={self.task_id}")
                self.request_user_auth(str(log_message.id))
        return True

    def construct_base_prompt(self):
        goals_clause = "\n".join(
            [f"{i+1}. {goal['description']}" for i, goal in enumerate(self.task.goals)]
        )
        commands_clause = self.command_registry.command_prompt()
        agent = self.agent
        from ix.agents.prompts import CONSTRAINTS_CLAUSE
        from ix.agents.prompts import RESOURCES_CLAUSE
        from ix.agents.prompts import SELF_EVALUATION_CLAUSE
        from ix.agents.prompts import FORMAT_CLAUSE

        return f"""
You are {agent.name}, {agent.purpose}
{goals_clause}
{CONSTRAINTS_CLAUSE}
{commands_clause}
{RESOURCES_CLAUSE}
{SELF_EVALUATION_CLAUSE}
{FORMAT_CLAUSE}
"""

    def log_exception(
        self,
        exception: Exception,
        think_msg: TaskLogMessage,
    ):
        """Collection point for errors while ticking the loop"""
        assert isinstance(exception, Exception), exception
        error_type = type(exception).__name__
        failure_msg = TaskLogMessage.objects.create(
            task_id=self.task_id,
            parent_id=think_msg.id,
            role="system",
            content={
                "type": "EXECUTE_ERROR",
                "message_id": str(message_id),
                "error_type": error_type,
                "text": str(exception),
            },
        )
        logger.error(
            f"@@@@ EXECUTE ERROR logged as id={failure_msg.id} message_id={message_id} error_type={error_type}"
        )
        logger.error(f"@@@@ EXECUTE ERROR {failure_msg.content['text']}")

    def handle_response(self, response: str) -> Dict[str, Any]:
        # find the json
        start_marker = "###START###"
        end_marker = "###END###"
        start_index = response.find(start_marker)
        end_index = response.find(end_marker)

        if start_index == -1 or end_index == -1:
            # before raising attempt to parse the response as json
            # sometimes the AI returns responses that are still usable even without the markers
            try:
                data = json.loads(response)
            except Exception:
                raise MissingCommandMarkers
        else:
            json_slice = response[start_index + len(start_marker) : end_index].strip()
            data = json.loads(json_slice)

        logger.debug(f"parsed message={data}")
        return data

    def build_prompt(self, user_input: str) -> PromptBuilder:
        assert user_input, "user_input is required"
        prompt = PromptBuilder(3000)

        # Add system prompt
        system_prompt = {"role": "system", "content": self.construct_base_prompt()}
        prompt.add(system_prompt)

        # Reinforcement
        reinforcement = [
            {
                "role": "user",
                "content": "respond with the expected format",
            },
            {"role": "assistant", "content": COMMAND_FORMAT},
        ]
        for msg in reinforcement:
            prompt.add(msg)

        # Add Memories
        memories = self.memory.find_nearest(str(self.history[-5:]), num_results=10)
        logger.debug(f"selected len={len(memories)} memories for prompt")
        prompt.add_max(memories, max_tokens=2500)

        # User prompt
        user_prompt = {"role": "user", "content": user_input}
        user_prompt_length = prompt.count_tokens([user_prompt])

        # Add history
        logger.debug(f"history contains n={len(self.history)}")
        prompt.add_max(self.history, max_tokens=500 - user_prompt_length)

        # add user prompt
        prompt.add(user_prompt)

        return prompt

    def parse_response(
        self, think_msg: TaskLogMessage, response: str
    ) -> Dict[str, Any]:
        # find the json
        start_marker = "###START###"
        end_marker = "###END###"
        start_index = response.find(start_marker)
        end_index = response.find(end_marker)

        if start_index == -1 or end_index == -1:
            # before raising attempt to parse the response as json
            # sometimes the AI returns responses that are still usable even without the markers
            try:
                data = json.loads(response.strip())
            except Exception as e:
                raise MissingCommandMarkers
        else:
            json_slice = response[start_index + len(start_marker) : end_index].strip()
            data = json.loads(json_slice)

        logger.debug(f"parsed message={data}")
        return data

    def handle_response(self, execute: bool, response: Dict[str, Any]):
        raise NotImplementedError(
            "Agents must implement handle_response for the specific type of response they receive"
        )

    def chat_with_ai(self, user_input) -> Tuple[TaskLogMessage, str]:
        prompt = self.build_prompt(user_input)
        agent = self.task.agent
        logger.info(f"Sending request to model {agent.model}")
        think_msg = TaskLogMessage.objects.create(
            task_id=self.task_id,
            role="system",
            content={
                "type": "THINK",
                "input": user_input,
            },
        )
        start = time.time()
        response = openai.ChatCompletion.create(
            model=agent.model,
            messages=prompt.messages,
            temperature=agent.config["temperature"],
            max_tokens=1000,
        )
        end = time.time()
        TaskLogMessage.objects.create(
            task_id=self.task_id,
            role="system",
            parent_id=think_msg.id,
            content={
                "type": "THOUGHT",
                "usage": response["usage"],
                "runtime": end - start,
            },
        )
        return think_msg, response["choices"][0]["message"]["content"]

    def add_history(self, *history_messages: Dict[str, Any]):
        logger.debug(f"adding history history_messages={history_messages}")
        self.history.extend(history_messages)

    def request_user_auth(self, message_id):
        """
        Request user input to authorize command.
        """
        TaskLogMessage.objects.create(
            task_id=self.task_id,
            role="assistant",
            content={
                "type": "AUTH_REQUEST",
                "message_id": message_id,
            },
        )
        # TODO: notify pubsub

    def msg_execute(self, cmd_message: TaskLogMessage):
        name = cmd_message.content["command"]["name"]
        kwargs = cmd_message.content["command"].get("args", {})
        try:
            result = self.execute(name, **kwargs)
            TaskLogMessage.objects.create(
                task_id=self.task_id,
                role="assistant",
                parent=cmd_message.parent,
                content={
                    "type": "EXECUTED",
                    "message_id": str(cmd_message.id),
                    "output": f"{name} executed, result={result}",
                },
            )
        except Exception as e:
            self.log_exception(e, cmd_message.parent, cmd_message)
        return True

    def execute(self, name: str, **kwargs) -> Any:
        """
        execute the command
        """
        logger.info(f"executing task_id={self.task_id} command={name} kwargs={kwargs}")
        result = self.command_registry.call(name, **kwargs)
        return result
