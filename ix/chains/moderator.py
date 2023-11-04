import logging
from typing import Dict, List, Optional, Any

from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.schema.runnable import Runnable, patch_config

from ix.chains.callbacks import IxHandler
from langchain.chains.base import Chain
from pydantic import BaseModel

from ix.chat.models import Chat
from ix.task_log.models import Task
from ix.task_log.tasks.agent_runner import start_agent_loop

logger = logging.getLogger(__name__)


MODERATOR_PROMPT = """
You are Ix, an AI assistant. You assist you user with requests by delegating work
to your team of agents.

Respond to all questions for help about Ix and how you work with links to discord and github.
The github includes documentation and source code.

discord: https://discord.gg/jtrMKxzZZQ
github: https://github.com/kreneskyp/ix

AGENTS:
{agents}

CHAT_HISTORY:
{chat_history}

INSTRUCTION:
- Choose the agent from AGENTS who can best process the user request.
- If no AGENT can process then respond as best you can.
- You must choose an agent or respond to the user request.
- Consider the CHAT_HISTORY in your decisions.
"""

CHOOSE_AGENT_PARAMS = {
    "type": "object",
    "properties": {
        "agents": {
            "type": "string",
        }
    },
    "required": ["agents"],
}


class ChooseAgent(BaseModel):
    agent_id: int


CHOOSE_AGENT_FUNC = {
    "class_path": "ix.chains.functions.FunctionSchema",
    "config": {
        "name": "delegate_to_agent",
        "description": "delegate the user request to this agent.",
        "parameters": ChooseAgent.schema_json(indent=4),
    },
}


LLM_CHOOSE_AGENT_CONFIG = {
    "class_path": "ix.chains.llm_chain.LLMChain",
    "config": {
        "verbose": True,
        "output_key": "delegation_or_text",
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
            "config": {
                "model": "gpt-4-0613",
                "request_timeout": 240,
                "temperature": 0,
                "verbose": True,
                "max_tokens": 1000,
                "streaming": True,
            },
        },
        "prompt": {
            "class_path": "langchain.prompts.chat.ChatPromptTemplate",
            "config": {
                "messages": [
                    {
                        "role": "assistant",
                        "template": MODERATOR_PROMPT,
                        "input_variables": ["agents", "chat_history"],
                    },
                    {
                        "role": "user",
                        "template": "{user_input}",
                        "input_variables": ["user_input"],
                    },
                ]
            },
        },
        "functions": [CHOOSE_AGENT_FUNC],
        "output_parser": {
            "class_path": "ix.chains.functions.OpenAIFunctionParser",
            "config": {
                "parse_json": True,
            },
        },
    },
}


class ChatModerator(Chain):
    """
    Chain that compares user input to a list of agents and chooses the best agent to handle the task
    """

    selection_chain: Runnable

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

    def agent_prompt(self, chat: Chat) -> str:
        """build prompt for configured tools"""
        lines = []
        agents = chat.agents.all().order_by("alias")
        for i, agent in enumerate(agents):
            lines.append(f"{i}. {agent.alias}: {agent.purpose}")
        return "\n".join(lines)

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        # 0. get chat and agents
        chat_id = inputs["chat_id"]
        chat = Chat.objects.get(id=chat_id)
        agents = list(chat.agents.order_by("alias"))

        # 1. select agent
        agent_prompt = "\n".join(
            [f"{i}. {agent.alias}: {agent.purpose}" for i, agent in enumerate(agents)]
        )
        user_input = inputs["user_input"]
        logger.debug(f"Routing user_input={user_input}")
        inputs_mutable = inputs.copy()
        inputs_mutable["agents"] = agent_prompt
        response = self.selection_chain.invoke(
            input=inputs_mutable,
            config=patch_config(config=None, callbacks=run_manager.get_child()),
        )
        delegation_or_text = response["delegation_or_text"]
        logger.debug(f"Moderator returned response={delegation_or_text}")

        # response is either a delegation or a direct text response
        if isinstance(delegation_or_text, dict):
            agent_index = delegation_or_text["arguments"]["agent_id"]
            delegate_to = agents[agent_index].alias
            text = f"Delegating to @{delegate_to}"
        else:
            text = delegation_or_text
            delegate_to = None

        # 2. send message to chat
        ix_handler = IxHandler.from_manager(run_manager)
        ix_handler.send_agent_msg(text)

        # 3. delegate to the agent
        task_id = None
        if delegate_to is not None:
            agent = chat.agents.get(alias=delegate_to)
            subtask = chat.task.delegate_to_agent(agent)
            logger.debug(
                f"Delegated to agent={agent.alias} task={subtask.id} input={inputs}"
            )
            start_agent_loop.delay(
                task_id=str(subtask.id), chain_id=str(agent.chain_id), inputs=inputs
            )
            task_id = str(subtask.id)

        return {"text": text, "task_id": task_id}

    async def _acall(
        self,
        inputs: Dict[str, str],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        # 0. get chat and agents
        chat_id = inputs["chat_id"]
        chat = await Chat.objects.aget(id=chat_id)
        agents = [value async for value in chat.agents.order_by("alias").aiterator()]

        # 1. select agent
        agent_prompt = "\n".join(
            [f"{i}. {agent.alias}: {agent.purpose}" for i, agent in enumerate(agents)]
        )
        user_input = inputs["user_input"]
        logger.debug(f"Routing user_input={user_input}")
        inputs_mutable = inputs.copy()
        inputs_mutable["agents"] = agent_prompt
        response = await self.selection_chain.ainvoke(
            input=inputs_mutable,
            config=patch_config(config=None, callbacks=run_manager.get_child()),
        )
        delegation_or_text = response["delegation_or_text"]
        logger.debug(f"Moderator returned response={delegation_or_text}")

        # response is either a delegation or a direct text response
        if isinstance(delegation_or_text, dict):
            agent_index = delegation_or_text["arguments"]["agent_id"]
            delegate_to = agents[agent_index].alias
            text = f"Delegating to @{delegate_to}"
        else:
            text = delegation_or_text
            delegate_to = None

        # 2. send message to chat
        ix_handler = IxHandler.from_manager(run_manager)
        await ix_handler.send_agent_msg(text)

        # 3. delegate to the agent
        task_id = None
        if delegate_to is not None:
            task = await Task.objects.aget(id=chat.task_id)
            agent = await chat.agents.aget(alias=delegate_to)
            subtask = await task.adelegate_to_agent(agent)
            logger.debug(
                f"Delegated to agent={agent.alias} task={subtask.id} input={inputs}"
            )
            start_agent_loop.delay(
                task_id=str(subtask.id), chain_id=str(agent.chain_id), inputs=inputs
            )
            task_id = str(subtask.id)

        return {"text": text, "task_id": task_id}
