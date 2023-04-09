from functools import cached_property
from typing import TypedDict, Optional


# AUTO GPT
from auto_gpt.chat import chat_with_ai, create_chat_message
from auto_gpt.config import Config
from auto_gpt.memory import PineconeMemory
from auto_gpt.command_registry import CommandRegistry, Command
from auto_gpt import commands as auto_gpt_commands

from ix.task_log.models import Task, TaskLogMessage


class UserInput(TypedDict):
    authorized_ticks: int
    feedback: Optional[str]


class AgentProcess:
    INITIAL_INPUT = "Determine which next command to use, and respond using the format specified above:"
    NEXT_COMMAND = "GENERATE NEXT COMMAND JSON"

    def __init__(self, task_id, message_id: int = None):
        self.task_id = task_id
        self.message_history = None
        self.memory = None

        # AutoGPT init
        self.auto_gpt_cfg = Config()
        self.prompt = self.auto_gpt_cfg.construct_full_prompt()
        self.auto_gpt_cfg.ai_name = self.agent.name

        # agent init
        self.init_commands()

        # task int
        self.load_message_history()
        self.initialize_memory()

    @cached_property
    def task(self):
        return Task.objects.get(pk=self.task_id)

    @cached_property
    def agent(self):
        return self.task.agent

    def load_message_history(self):
        messages = TaskLogMessage.objects.filter(task_id=self.task_id).order_by(
            "-created_at"
        )
        self.message_history = [message.as_dict() for message in messages]

    def initialize_memory(self):
        # api key set via env variables
        # PINE_CONE_API_KEY and PINECONE_ENV
        self.memory = PineconeMemory()
        self.memory.clear()

    def init_commands(self):
        """Load commands for this agent"""
        self.command_registry = CommandRegistry()
        self.command_registry.import_commands("auto_gpt.ai_functions")
        self.command_registry.import_commands("auto_gpt.commands")
        self.command_registry.import_commands("auto_gpt.execute_code")
        self.command_registry.import_commands("auto_gpt.agent_manager")
        self.command_registry.import_commands("auto_gpt.file_operations")

    def start(self, n: int = 1, user_input_msg: TaskLogMessage = None) -> None:
        """
        start agent loop and process `n` ticks. Pass `input` to resume from user feedback.
        """

        tick_input = None
        if user_input_msg:
            tick_input = user_input_msg.content
        elif self.message_history.length == 0:
            # special first input for loop start
            tick_input = self.INITIAL_INPUT

        # if there is initial input, tick once
        if tick_input:
            self.tick(tick_input)

        # run the remainder of authorized ticks in a loop
        # set auto-execute here.
        if n > 1:
            for i in range(1, n):
                self.tick(execute=True)

    def tick(self, input=NEXT_COMMAND, execute=False):
        """
        "tick" the agent loop letting it chat and run commands
        """
        response = self.chat_with_ai(input)
        command, kwargs = self.handle_response(response)

        if command:
            command = self.command_registry(response.command)
            if execute:
                result = self.execute(command)
                self.message_history.append(create_chat_message("system", result))
            else:
                self.request_user_input()

    def handle_response(self, message):
        command_name, arguments = auto_gpt_commands.parse_command(message)
        command = self.command_registry.get(command_name)
        return command, arguments

    def chat_with_ai(self, input):
        return chat_with_ai(
            self.prompt,
            input,
            full_message_history=self.message_history,
            permanent_memory=self.memory,
            token_limit=self.auto_gpt_cfg.fast_token_limit,
        )

    def request_user_input(self):
        """
        Request user input to complete task.
        """
        TaskLogMessage.objects.create(
            role="system", content="requesting user authorization and input"
        )
        # TODO: notify pubsub

    def execute(self, command: Command, **kwargs):
        """
        execute the command
        """
        return command.execute(**kwargs)
