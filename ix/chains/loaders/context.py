import asyncio
import logging
from datetime import datetime
from typing import Callable, Dict, Optional
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db.models import Q
from langchain.schema.runnable.utils import Input
from pydantic import BaseModel

from ix.chat.models import Chat
from ix.runnable_log.models import RunnableExecution
from ix.runnable_log.subscription import RunEventSubscription
from ix.task_log.models import Task
from ix.utils.json import to_json_serializable

logger = logging.getLogger(__name__)


def now() -> datetime:
    """Return timezone aware timestamp in milliseconds."""
    timezone = ZoneInfo("America/New_York")
    return datetime.now(timezone)


class Listener:
    node_id: UUID
    run: dict = {}

    def __init__(self, context: "IxContext", parent: Optional["Listener"] = None):
        self.context = context
        self.node_id = node_id

    def on_start(self, input: Input) -> None:
        self.run = {
            "id": str(uuid4()),
            "user_id": str(self.context.user_id),
            "task_id": str(self.context.task_id),
            "node_id": str(self.node_id),
            "started_at": datetime.now(tz=ZoneInfo("America/Los_Angeles")),
            "inputs": to_json_serializable(input),
            "completed": False,
        }

        RunEventSubscription.on_execution(
            chain_id=self.context.chain_id,
            event=self.run,
        )

    def on_end(self, output):
        self.log_run(input, output, completed=True)
        pass

    async def aon_end(self, output):
        await self.alog_run(output, completed=True)
        pass

    async def on_error(self, exception: Exception):
        await self.alog_run(output={}, message=str(exception), completed=False)

    async def alog_run(self, output, message: str = None, completed: bool = True):
        if not settings.RUNNABLE_LOG_ENABLED:
            return

        self.run.update(
            dict(
                completed=completed,
                message=message,
                outputs=to_json_serializable(output),
                finished_at=datetime.now(tz=ZoneInfo("America/Los_Angeles")),
            )
        )
        await asyncio.gather(
            RunEventSubscription.aon_execution(
                chain_id=self.context.chain_id,
                event=self.run,
            ),
            RunnableExecution.objects.acreate(**self.run),
        )

    @property
    def callbacks(self) -> Dict[str, Callable]:
        return {
            "on_start": self.on_start,
            "on_end": self.on_end,
            "on_error": self.on_error,
        }


class IxContext(BaseModel):
    """
    Context for an execution of a runnable. This is a connection point between the runnable and
    IX services.

    Includes references to the task, agent, chain, and user who initiated the request. Also
    provides a listener and eventually other client callbacks.
    """

    agent_id: str
    chain_id: str
    task_id: str
    user_id: str
    chat_id: Optional[str] = None

    def get_listener(self, node_id: UUID) -> Listener:
        return Listener(self, node_id=node_id)

    @classmethod
    def from_task(cls, **kwargs) -> "IxContext":
        kwargs = kwargs.copy()

        if "task" in kwargs:
            task = kwargs.pop("task")
            kwargs["task_id"] = str(task.id)
        elif "task_id" in kwargs:
            task = Task.objects.get(id=kwargs["task_id"])
            kwargs["task_id"] = str(kwargs["task_id"])
        else:
            raise ValueError("task or task_id must be provided")

        # auto configure from task if not provided values
        if "agent_id" not in kwargs:
            kwargs["agent_id"] = str(task.agent_id)
        if "chain_id" not in kwargs:
            kwargs["chain_id"] = str(task.chain_id)
        if "user_id" not in kwargs:
            kwargs["user_id"] = str(task.user_id)

        if "chat_id" not in kwargs:
            root_id = task.root_id if task.root_id else task.id
            try:
                chat = Chat.objects.get(task_id=root_id)
                kwargs["chat_id"] = str(chat.id)
            except Chat.DoesNotExist:
                pass

        return cls(**kwargs)

    @classmethod
    async def afrom_task(cls, **kwargs) -> "IxContext":
        kwargs = kwargs.copy()

        if "task" in kwargs:
            task = kwargs.pop("task")
            kwargs["task_id"] = str(task.id)
        elif "task_id" in kwargs:
            task = await Task.objects.aget(id=kwargs["task_id"])
            kwargs["task_id"] = str(kwargs["task_id"])
        else:
            raise ValueError("task or task_id must be provided")

        # auto configure from task if not provided values
        if "agent_id" not in kwargs:
            kwargs["agent_id"] = str(task.agent_id)
        if "chain_id" not in kwargs:
            kwargs["chain_id"] = str(task.chain_id)
        if "user_id" not in kwargs:
            kwargs["user_id"] = str(task.user_id)

        if "chat_id" not in kwargs:
            try:
                chat = await Chat.objects.aget(Q(task=task) | Q(task_id=task.parent_id))
                kwargs["chat_id"] = str(chat.id)
            except Chat.DoesNotExist:
                pass

        return cls(**kwargs)
