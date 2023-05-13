import logging
from typing import Dict, Any, List

from langchain import LLMChain
from langchain.chains.base import Chain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import BaseLanguageModel

from ix.agents.callback_manager import IxCallbackManager
from ix.agents.llm import load_llm
from ix.agents.models import Agent
from ix.chains.json import parse_json
from ix.chat.models import Chat
from ix.task_log.models import Task
from ix.task_log.tasks.agent_runner import start_agent_loop


logger = logging.getLogger(__name__)


MODERATOR_PROMPT = """
You are a chat moderator. You direct messages to the agent who can best response to the user request

AGENTS:
{agents}

AGENT_FORMAT:
###START###
{{"agent": "agent_name"}}
###END###

QUESTION_FORMAT:
###START###
{{"question": "question text"}}
###END###

INSTRUCTION:
- Choose the agent from AGENTS who will process the user request.
- Respond in AGENT_FORMAT if returning an AGENT.
- If no AGENT can process the request, respond with QUESTION_FORMAT for a clarifying QUESTION.
- DO NOT ADD EXTRA FIELDS TO THE EXPECTED FORMAT
"""


class LLMChooseAgent(LLMChain):
    """Chain that selects an agent using the descriptions of the agents."""

    output_key = "agent"

    @property
    def input_keys(self) -> List[str]:
        """Input keys this chain expects."""
        return ["user_input"]

    @classmethod
    def from_llm(cls, llm: BaseLanguageModel, verbose: bool = True) -> LLMChain:
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            MODERATOR_PROMPT
        )
        human_template = "{user_input}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)


class ChatModerator(Chain):
    """
    Chain that compares user input to a list of tools and chooses the best tool to handle the task
    """

    llm: Any = None
    selection_chain: Chain = None
    callback_manager: Any = None

    def __init__(
        self,
        callback_manager: Any,
        selection_chain: Chain,
        **data,
    ):
        super().__init__(**data)
        self.selection_chain = selection_chain
        self.callback_manager = callback_manager
        self.llm = data["llm"]

    @property
    def _chain_type(self) -> str:
        return "ix_chat_moderator"

    @property
    def output_keys(self) -> List[str]:
        """Outputs task_id of spawned subtask"""
        return ["task_id"]

    @property
    def input_keys(self) -> List[str]:
        """Input keys this chain expects."""
        return ["user_input", "chat_id"]

    def agent_prompt(self, chat_id: str) -> str:
        """build prompt for configured tools"""
        chat = Chat.objects.get(id=chat_id)
        lines = []
        for i, agent in enumerate(chat.agents.all()):
            lines.append(f"{i}. {agent.alias}: {agent.purpose}")
        return "\n".join(lines)

    def delegate_to_agent(self, agent_id, user_input):
        task = self.callback_manager.task
        agent = Agent.objects.get(id=agent_id)
        subtask = Task.objects.create(
            parent=task,
            name="subtask: ",
            agent_id=agent_id,
            autonomous=task.autonomous,
        )
        start_agent_loop.delay(
            task_id=subtask.id, chain_id=agent.chain_id, user_input=user_input
        )
        return subtask.id

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        # 1. select agent
        user_input = inputs["user_input"]
        chat_id = inputs["chat_id"]
        logger.debug(f"Routing user_input={user_input}")
        response = self.selection_chain.run(
            user_input=user_input, agents=self.agent_prompt(chat_id)
        )
        logger.debug(f"Moderator returned response={response}")
        response_data = parse_json(response)

        # 1. delegate to the agent
        agent_name = response_data.pop("agent")
        task_id = self.delegate_to_agent(agent_name, inputs, response_data)
        return {"task_id": task_id}

    async def _acall(self, inputs: Dict[str, str]) -> Dict[str, str]:
        pass

    @classmethod
    def from_config(cls, config: Dict[str, Any], callback_manager: IxCallbackManager):
        """Load an instance from a config dictionary and runtime"""
        llm_config = config["llm"]
        llm = load_llm(llm_config, callback_manager)

        chooser = LLMChooseAgent.from_llm(llm=llm)
        chooser.callback_manager = callback_manager

        instance = cls(
            llm=llm,
            selection_chain=chooser,
            callback_manager=callback_manager,
        )
        instance.llm = llm
        return instance
