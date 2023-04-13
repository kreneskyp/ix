import logging
from functools import cached_property
from typing import TypedDict, Optional, Type, List


import openai

# AUTO GPT
from auto_gpt.json_parser import fix_and_parse_json

from ix.agents.prompt_builder import PromptBuilder
from ix.memory.plugin import VectorMemory
from ix.task_log.models import Task, TaskLogMessage
from ix.commands.registry import CommandRegistry, Command
from ix.utils.importlib import import_class
from ix.utils.types import ClassPath


AUTO_GPT_COMMANDS = [
    "auto_gpt.ai_functions",
    "auto_gpt.commands",
    "auto_gpt.execute_code",
    "auto_gpt.agent_manager",
    "auto_gpt.file_operations",
]


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
    INITIAL_INPUT = "Determine which next command to use, and respond using the format specified above:"
    NEXT_COMMAND = "GENERATE NEXT COMMAND JSON"

    command_registry: CommandRegistry

    def __init__(
        self,
        task_id: int,
        memory_class: ClassPath = "ix.memory.pinecone.PineconeMemory",
        command_classes: List[ClassPath] = AUTO_GPT_COMMANDS,
    ):
        logger.info(f"AgentProcess initializing task_id={task_id}")

        # agent config
        self.memory_class = memory_class
        self.command_classes = command_classes

        # initial state
        self.task_id = task_id
        self.history = []
        self.last_message_at = None
        self.memory = None

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
        excluded_content_types = ["FEEDBACK_REQUEST"]
        query = (
            TaskLogMessage.objects.filter(task_id=self.task_id)
            .exclude(content__type__in=excluded_content_types)
            .order_by("created_at")
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
            self.last_message_at = messages[0].created_at

        formatted_messages = [message.as_message() for message in messages]
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
        for class_path in self.command_classes:
            self.command_registry.import_commands(class_path)

        logger.info(f"intialized command registry")

    def start(self, n: int = 1, user_input_msg: TaskLogMessage = None) -> None:
        """
        start agent loop and process `n` ticks. Pass `input` to resume from user feedback.
        """
        logger.info(f"starting process loop task_id={self.task_id}")
        tick_input = None
        if user_input_msg:
            logger.info(f"resuming with user input for task_id={self.task_id}")
            tick_input = user_input_msg.content["feedback"]
        elif len(self.history) == 0:
            # special first input for loop start
            logger.info(f"first tick for task_id={self.task_id}")
            tick_input = self.INITIAL_INPUT

        # if there is input, tick once
        if tick_input:
            self.tick(tick_input)

        # run the remainder of authorized ticks in a loop
        # set auto-execute here.
        if n > 1:
            for i in range(1, n):
                self.tick(execute=True)

    def tick(self, user_input=NEXT_COMMAND, execute=False):
        """
        "tick" the agent loop letting it chat and run commands
        """
        logger.info(f"ticking task_id={self.task_id}")
        response = self.chat_with_ai(user_input)
        logger.debug(f"Response from model, task_id={self.task_id} response={response}")
        data = self.handle_response(response)

        # save to persistent storage
        TaskLogMessage.objects.create(
            task_id=self.task_id,
            role="assistant",
            content=dict(type="ASSISTANT", **data),
        )

        # process command and then execute or seek feedback
        command_name = data["command"]["name"]
        command_kwargs = data["command"].get("args", {})
        command = self.command_registry.get(command_name)
        logger.info(f"model returned task_id={self.task_id} command={command.name}")
        if command:
            if execute:
                result = self.execute(command, **command_kwargs)
                self.history.append(ChatMessage(role="system", content=result))
            else:
                logger.info(f"requesting user input task_id={self.task_id}")
                self.request_user_input()

    def construct_prompt(self):
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

    def handle_response(self, message):
        data = fix_and_parse_json(message)
        logger.debug(f"parsed message={data}")
        command_name = data["command"]["name"]
        return data

    def chat_with_ai(self, user_input):
        prompt = PromptBuilder(3000)

        system_prompt = {"role": "system", "content": self.construct_prompt()}
        user_prompt = {"role": "user", "content": user_input}

        # Add system prompt
        prompt.add(system_prompt)

        # Add Memories
        memories = self.memory.find_nearest(str(self.history[-5:]), num_results=10)
        prompt.add_max(memories, max_tokens=2500)

        # Add history
        user_prompt_length = prompt.count_tokens([user_prompt])
        prompt.add_max(reversed(self.history), max_tokens=500 - user_prompt_length)

        # add user prompt
        prompt.add(user_prompt)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt.messages,
            temperature=0.6,
            max_tokens=1000,
        )
        return response["choices"][0]["message"]["content"]

    def request_user_input(self):
        """
        Request user input to complete task.
        """
        TaskLogMessage.objects.create(
            task_id=self.task_id,
            role="system",
            content={
                "type": "FEEDBACK_REQUEST",
                "message": "requesting user authorization and input",
            },
        )
        # TODO: notify pubsub

    def execute(self, command: Command, **kwargs):
        """
        execute the command
        """
        logger.info(
            f"executing task_id={self.task_id} command={command.name} kargs={kwargs}"
        )

        return command(**kwargs)
