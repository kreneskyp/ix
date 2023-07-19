import logging
import time
import traceback
from functools import cached_property
from typing import Dict, Union, Any, List, Optional
from uuid import UUID

from channels.layers import get_channel_layer
from django.db.models import Q
from langchain.callbacks.manager import AsyncCallbackManagerForChainRun

from ix.chat.models import Chat
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import AgentAction, BaseMessage

from ix.agents.models import Agent
from ix.chains.models import Chain
from ix.task_log.models import Task, TaskLogMessage


logger = logging.getLogger(__name__)


class IxHandler(AsyncCallbackHandler):
    task: Task = None
    chain: Chain = None
    agent: Agent = None
    parent_think_msg = None
    think_msgs = {}

    def __init__(self, agent: Agent, chain: Chain, task: Task, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = agent
        self.chain = chain
        self.task = task
        self.channel_layer = get_channel_layer()
        self.channel_name = f"{self.task.id}_stream"

    @property
    def user_id(self) -> str:
        # HAX: this is currently always the owner of the chat. Likely need to update
        # this in the future to be the user making the request.
        return str(self.task.user_id)

    @cached_property
    def chat_id(self) -> str:
        try:
            chat = Chat.objects.get(Q(task=self.task) | Q(task_id=self.task.parent_id))
        except Chat.DoesNotExist:
            return None
        return chat.id

    async def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Any:
        pass

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        pass

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        # streaming to be implemented in a later PR
        pass

    async def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when LLM errors."""

    async def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when chain starts running."""

        if not self.parent_think_msg:
            self.start = time.time()
            think_msg = await TaskLogMessage.objects.acreate(
                task_id=self.task.id,
                role="system",
                content={"type": "THINK", "input": inputs, "agent": self.agent.alias},
            )
            self.parent_think_msg = think_msg

    async def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        # only record the final thought for now
        if not parent_run_id:
            await TaskLogMessage.objects.acreate(
                task_id=self.task.id,
                role="system",
                parent_id=self.parent_think_msg.id,
                content={
                    "type": "THOUGHT",
                    # TODO: hook usage up, might be another signal though.
                    # "usage": response["usage"],
                    "runtime": time.time() - self.start,
                },
            )

    async def on_chain_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when chain errors."""
        assert isinstance(error, Exception), error
        traceback_list = traceback.format_exception(
            type(error), error, error.__traceback__
        )
        traceback_string = "".join(traceback_list)
        error_type = type(error).__name__
        think_msg_id = self.parent_think_msg.id if self.parent_think_msg else None
        failure_msg = await TaskLogMessage.objects.acreate(
            task_id=self.task.id,
            parent_id=think_msg_id,
            role="assistant",
            content={
                "type": "EXECUTE_ERROR",
                "error_type": error_type,
                "text": str(error),
                "details": traceback_string,
            },
        )
        logger.error(
            f"@@@@ EXECUTE ERROR logged as id={failure_msg.id} message_id={think_msg_id} error_type={error_type}"
        )
        logger.error(f"@@@@ EXECUTE ERROR {failure_msg.content['text']}")

    async def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        pass

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        pass

    async def send_chat_message(self, message_id: str, text: str) -> None:
        """
        Stream message fragment to the chat.
        """
        await self.channel_layer.send(
            # self.channel_name, {"type": "msg", "message_id": message_id, "text": text}
            self.channel_name,
            [message_id, text],
        )

    async def send_agent_msg(self, text: str) -> None:
        """
        Send a message to the agent.
        """
        await TaskLogMessage.objects.acreate(
            task_id=self.task.id,
            role="assistant",
            parent=self.parent_think_msg,
            content={
                "type": "ASSISTANT",
                "text": text,
                "agent": self.agent.alias,
            },
        )

    @staticmethod
    def from_manager(run_manager: AsyncCallbackManagerForChainRun):
        """Helper method for finding the IxHandler in a run_manager."""
        ix_handlers = [
            handler
            for handler in run_manager.handlers
            if isinstance(handler, IxHandler)
        ]
        if len(ix_handlers) == 0:
            raise ValueError("Expected at least one IxHandler in run_manager")
        if len(ix_handlers) != 1:
            raise ValueError("Expected exactly one IxHandler in run_manager")
        return ix_handlers[0]
