import logging
import json
import openai
from functools import cached_property
from typing import TypedDict, Optional, List, Any, Dict

from ix.agents.prompt_builder import PromptBuilder
from ix.agents.prompts import COMMAND_FORMAT
from ix.memory.plugin import VectorMemory
from ix.task_log.models import Task, TaskLogMessage
from ix.commands.registry import CommandRegistry
from ix.utils.importlib import import_class
from ix.utils.types import ClassPath


class MissingCommandMarkers(Exception):
    """Exception thrown when command markers are missing from response"""


# config defaults
DEFAULT_COMMANDS = [
    "ix.commands.google",
    "ix.commands.filesystem",
    "ix.commands.execute",
]
DEFAULT_MEMORY = "ix.memory.redis.RedisVectorMemory"
DEFAULT_MEMORY_OPTIONS = {"host": "redis"}


# logging
FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(format=FORMAT, level="DEBUG")
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
        "FEEDBACK_REQUEST",
        "AUTH_REQUEST",
        "EXECUTED",
        "AUTHORIZE",
        "AUTONOMOUS",
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
        Update message history for the most recent messages. Will query only new messages
        if agent already contains messages
        """

        # fetch unseen messages and save the last timestamp for the next iteration
        messages = list(self.query_message_history(self.last_message_at))
        if messages:
            self.last_message_at = messages[-1].created_at

        # toggle autonomous mode based on newest AUTONOMOUS message
        for message in messages:
            if message.content["type"] == "AUTONOMOUS":
                self.autonomous = message.content["enabled"]

        formatted_messages = [
            message.as_message()
            for message in messages
            if message.content["type"] not in self.EXCLUDED_MSG_TYPES
        ]
        self.history.extend(formatted_messages)

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

        logger.info(f"intialized command registry")

    def start(self, n: int = 0) -> None:
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
            logger.info(f"resuming with user input for task_id={self.task_id}")
            # auth/feedback resume, run command that was authorized
            authorized_for = last_message.content["n"] - 1
            authorized_msg = TaskLogMessage.objects.get(
                pk=last_message.content["message_id"]
            )
            self.msg_execute(authorized_msg)
        elif last_message.content["type"] in ["AUTH_REQUEST", "FEEDBACK_REQUEST"]:
            # if last message is an unfulfilled feedback request then exit
            logger.info(
                f"Exiting, missing response to type={last_message.content['type']}"
            )
            return

        # pass to main loop
        self.loop(n=authorized_for, tick_input=tick_input)

    def loop(self, n=1, tick_input: str = None):
        for i in range(n + 1):
            execute = self.autonomous or i < n
            self.tick(execute=execute)

    def tick(self, user_input: str = NEXT_COMMAND, execute: bool = False):
        """
        "tick" the agent loop letting it chat and run commands
        """
        logger.debug("============================================================================")
        logger.info(f"ticking task_id={self.task_id}")
        logger.info(f"ticking task_id={self.task_id}")
        response = self.chat_with_ai(user_input)
        logger.debug(f"Response from model, task_id={self.task_id} response={response}")
        data = self.handle_response(response)

        # if bot asks a question then log it and exit.
        if "question" in data:
            TaskLogMessage.objects.create(
                task_id=self.task_id,
                role="assistant",
                content=dict(type="FEEDBACK_REQUEST", question=data["question"]),
            )
            return

        # log command to persistent storage
        log_message = TaskLogMessage.objects.create(
            task_id=self.task_id,
            role="assistant",
            content=dict(type="ASSISTANT", **data),
        )

        # validate command and then execute or seek feedback
        if (
            not "command" in data
            or not "name" in data["command"]
            or not "args" in data["command"]
            or not data["command"]
        ):
            TaskLogMessage.objects.create(
                task_id=self.task_id,
                role="user",
                content={
                    "type": "EXECUTE_ERROR",
                    "message_id": log_message.id,
                    "error_type": "missing command",
                    "text": f"respond in the expected format",
                },
            )
        elif data["command"]["name"] not in self.command_registry.commands:
            TaskLogMessage.objects.create(
                task_id=self.task_id,
                role="user",
                content={
                    "type": "EXECUTE_ERROR",
                    "message_id": log_message.id,
                    "error_type": "unknown command",
                    "text": f'{data["command"]["name"]} is not available',
                },
            )
        else:
            command = self.command_registry.get(data["command"]["name"])
            logger.info(f"model returned task_id={self.task_id} command={command.name}")
            if execute:
                try:
                    self.msg_execute(log_message)
                except Exception as e:
                    error_context = (
                        f'{data["command"]["name"]}: {data["command"]["args"]}'
                    )
                    self.save_and_raise(log_message, error_context, user_input, e)
            else:
                logger.info(f"requesting user authorization task_id={self.task_id}")
                self.request_user_auth(log_message.id)

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

    def save_and_raise(
        self,
        log_msg: TaskLogMessage,
        context: str,
        user_input: str,
        exception: Exception,
    ):
        """Collection point for errors while ticking the loop"""
        prompt = self.build_prompt(user_input)
        failure_msg = TaskLogMessage.objects.create(
            task_id=self.task_id,
            role="system",
            content={
                "type": "EXECUTE_ERROR",
                "message_id": log_msg.id,
                "error_type": type(exception).__name__,
                "text": str(exception),
            },
        )
        logger.error(f"@@@@ EXECUTE ERROR logged as id={failure_msg.id}")

    def handle_response(self, response: str) -> Dict[str, Any]:
        # find the json
        start_marker = "###START###"
        end_marker = "###END###"
        start_index = response.find(start_marker)
        end_index = response.find(end_marker)

        if start_index == -1 or end_index == -1:
            raise MissingCommandMarkers

        json_slice = response[start_index + len(start_marker) : end_index].strip()
        data = json.loads(json_slice)

        logger.debug(f"parsed message={data}")
        return data

    def build_prompt(self, user_input: str) -> PromptBuilder:
        assert user_input, f"user_input is required"
        prompt = PromptBuilder(3000)

        system_prompt = {"role": "system", "content": self.construct_base_prompt()}
        reinforcement_query = {
            "role": "user",
            "content": "respond with the expected format",
        }
        reinforcement_response = {"role": "assistant", "content": COMMAND_FORMAT}

        # Add system prompt
        prompt.add(system_prompt)
        prompt.add(reinforcement_query)
        prompt.add(reinforcement_response)

        # Add Memories
        memories = self.memory.find_nearest(str(self.history[-5:]), num_results=10)
        prompt.add_max(memories, max_tokens=2500)

        # User prompt
        user_prompt = {"role": "user", "content": user_input}
        user_prompt_length = prompt.count_tokens([user_prompt])

        # Add history
        prompt.add_max(self.history, max_tokens=500 - user_prompt_length)

        # add user prompt
        prompt.add(user_prompt)

        return prompt

    def chat_with_ai(self, user_input):
        prompt = self.build_prompt(user_input)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt.messages,
            temperature=0.2,
            max_tokens=1000,
        )
        return response["choices"][0]["message"]["content"]

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

    def msg_execute(self, message: TaskLogMessage):
        name = message.content["command"]["name"]
        kwargs = message.content["command"].get("args", {})
        result = self.execute(name, **kwargs)
        TaskLogMessage.objects.create(
            task_id=self.task_id,
            role="assistant",
            content={
                "type": "EXECUTED",
                "message_id": message.id,
            },
        )
        return result

    def execute(self, name: str, **kwargs) -> Any:
        """
        execute the command
        """
        logger.info(f"executing task_id={self.task_id} command={name} kwargs={kwargs}")
        result = self.command_registry.call(name, **kwargs)
        self.history.append(ChatMessage(role="system", content=result))
        return result
