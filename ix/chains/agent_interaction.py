import logging
from typing import Dict, Any, List, Optional

from langchain.schema import BasePromptTemplate

from ix.agents.models import Agent
from ix.chains.callbacks import IxHandler

from ix.chat.models import Chat
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains.base import Chain

from ix.task_log.models import Task
from ix.task_log.tasks import start_agent_loop


logger = logging.getLogger(__name__)


async def adelegate_task(chat: Chat, delegate_to: str, inputs: Dict[str, Any]):
    """Delegate a task to another agent

    This works by scheduling the worker process directly.
    TODO: update to use IX API. This temp solution is just MVP
    """
    task = await Task.objects.aget(id=chat.task_id)
    agent = await chat.agents.aget(alias=delegate_to)
    subtask = await task.adelegate_to_agent(agent)
    logger.debug(f"Delegated to agent={agent.alias} task={subtask.id} input={inputs}")

    start_agent_loop.delay(
        task_id=str(subtask.id),
        chain_id=str(agent.chain_id),
        inputs=inputs,
        user_id=str(subtask.user_id),
    )


class DelegateToAgentChain(Chain):
    """Delegate a task to another aget

    This task does not configure the reply. The agent must also use a `DelegateChain` to
    reply to the request.
    """

    # output key that records agent alias that was delegated to
    output_key: str = "delegate_to"

    # alias of agent to delegate to
    target_alias: str

    # prompt used to generate message sent to the target agent
    # The message will be sent as "user_input".  The target agent
    # will use this input to handle the request.
    prompt: BasePromptTemplate

    # inputs to include in the message sent to the target agent
    # along with the prompt generated user_input
    delegate_inputs: list = None

    @property
    def _chain_type(self) -> str:
        return "ix.delegate_chain"  # pragma: no cover

    @property
    def input_keys(self) -> List[str]:
        """Will be whatever keys the prompt expects.

        :meta private:
        """
        return self.prompt.input_variables

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError(
            "DelegateChain does not support sync calls"
        )  # pragma: no cover

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Run chain asynchronously"""
        # Get chat
        chat_id = inputs["chat_id"]
        chat = await Chat.objects.aget(id=chat_id)

        # Summon the agent to the chat if it is not already here
        is_agent_here = await chat.agents.filter(alias=self.target_alias).aexists()
        if not is_agent_here:
            target = await Agent.objects.aget(alias=self.target_alias)
            await chat.agents.aadd(target)

        # send message to chat to inform user
        text = f"Delegating to @{self.target_alias}"
        ix_handler = IxHandler.from_manager(run_manager)
        await ix_handler.send_agent_msg(text)

        # Generate inputs and send message to agent
        #    prompt has access to all inputs thus far
        if self.delegate_inputs is None:
            delegate_inputs = inputs.copy()
        else:
            delegate_inputs = {k: inputs[k] for k in self.delegate_inputs}
        prompt = self.prompt.format_prompt(**inputs)
        delegate_inputs["user_input"] = prompt.to_string()
        delegate_inputs["chat_id"] = inputs["chat_id"]
        await adelegate_task(chat, self.target_alias, delegate_inputs)

        # return as output_key
        return {self.output_key: text}
