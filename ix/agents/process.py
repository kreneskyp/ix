import logging
from typing import TypedDict, Optional, Any, Dict

from asgiref.sync import sync_to_async
from langchain.schema.runnable import RunnableConfig

from ix.agents.models import Agent
from ix.chains.callbacks import IxHandler
from ix.chains.models import Chain as ChainModel
from ix.task_log.models import Task


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
        start agent loop
        """
        logger.info(f"starting process loop task_id={self.task.id} input_id={inputs}")
        response = await self.chat_with_ai(inputs)
        logger.debug(f"Response from model, task_id={self.task.id} response={response}")
        return True

    async def chat_with_ai(self, user_input: Dict[str, Any]) -> Any:
        handler = IxHandler(agent=self.agent, chain=self.chain, task=self.task)

        try:
            # TODO: chain loading needs to be made async
            chain = await sync_to_async(self.chain.load_chain)(handler)

            logger.info(
                f"Sending request to chain={self.chain.name} prompt={user_input}"
            )

            # auto-map user_input to other input keys if not provided.
            # work around until chat input key can be configured per chain
            inputs = user_input.copy()
            if "input" not in inputs:
                inputs["input"] = user_input["user_input"]
            if "question" not in inputs:
                inputs["question"] = user_input["user_input"]

            return await chain.ainvoke(inputs, RunnableConfig(callbacks=[handler]))
        except Exception as e:
            # validation errors aren't caught by callbacks.
            await handler.send_error_msg(e)
            return None
