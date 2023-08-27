from typing import List, Dict, Any, Optional

from ix.chains.callbacks import IxHandler
from langchain.agents import AgentExecutor
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains.base import Chain

from ix.task_log.models import TaskLogMessage


class AgentReply(Chain):
    """
    An chain that wraps an AgentExecutor to capture the reply and send it to the
    chat using a TaskLogMessage.

    This chain is a workaround until replies are captured with chain callbacks.
    """

    agent_executor: AgentExecutor
    output_key: str = "output"
    reply: bool = True

    @property
    def _chain_type(self) -> str:
        return "agent_reply"

    @property
    def input_keys(self) -> List[str]:
        return []

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        pass

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        result = await self.agent_executor.acall(inputs, callbacks=run_manager)
        ix_handler = IxHandler.from_manager(run_manager)

        if self.reply:
            await TaskLogMessage.objects.acreate(
                task_id=ix_handler.task.id,
                role="ASSISTANT",
                parent=ix_handler.parent_think_msg,
                content={
                    "type": "ASSISTANT",
                    "text": result[self.output_key],
                    "agent": ix_handler.agent.alias,
                },
            )

        return result
