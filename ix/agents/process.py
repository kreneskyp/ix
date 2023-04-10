import logging
from functools import cached_property
from typing import TypedDict, Optional


# AUTO GPT
from auto_gpt.chat import chat_with_ai
from auto_gpt.memory import PineconeMemory
from auto_gpt import commands as auto_gpt_commands


from ix.task_log.models import Task, TaskLogMessage
from ix.commands.registry import CommandRegistry, Command

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

    def __init__(self, task_id, message_id: int = None):
        logger.info(f"AgentProcess initializing task_id={task_id}")
        self.task_id = task_id
        self.message_history = None
        self.memory = None

        # agent init
        self.init_commands()

        # task int
        self.load_message_history()
        self.initialize_memory()
        logger.info("AgentProcess initialized")

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
        logger.info(f"AgentProcess loaded n={len(self.message_history)} chat messages from history")

    def initialize_memory(self):
        # api key set via env variables
        # PINECONE_API_KEY and PINECONE_ENV
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
        logger.info(f"intialized command registry")

    def start(self, n: int = 1, user_input_msg: TaskLogMessage = None) -> None:
        """
        start agent loop and process `n` ticks. Pass `input` to resume from user feedback.
        """
        logger.info(f"starting process loop task_id={self.task_id}")

        tick_input = None
        if user_input_msg:
            logger.info(f"resuming with user input for task_id={self.task_id}")
            tick_input = user_input_msg.content['feedback']
        elif len(self.message_history) == 0:
            # special first input for loop start
            logger.info(f"first tick for task_id={self.task_id}")
            tick_input = self.INITIAL_INPUT

        # if there is input, tick once
        if tick_input:
            self.tick(tick_input)

        return

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

        # save to persistent storage
        TaskLogMessage.objects.create(
            task_id=self.task_id,
            role="assistant",
            content={
                'type': "ASSISTANT",
                'message': response
            }
        )

        # process command and then execute or seek feedback
        command, command_kwargs = self.handle_response(response)
        logger.info(f"model returned task_id={self.task_id} command={command.name}")
        if command:
            if execute:
                logger.info(f"executing task_id={self.task_id} command={command.name}")
                result = self.execute(command, **command_kwargs)
                self.message_history.append(ChatMessage(role="system", content=result))
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
        command_name, arguments = auto_gpt_commands.parse_command(message)
        command = self.command_registry.get(command_name)
        return command, arguments

    def chat_with_ai(self, input):
        return chat_with_ai(
            self.construct_prompt(),
            input,
            full_message_history=self.message_history,
            permanent_memory=self.memory,
            token_limit=4000,
        )

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
            }
        )
        # TODO: notify pubsub

    def execute(self, command: Command, **kwargs):
        """
        execute the command
        """
        return command.execute(**kwargs)
