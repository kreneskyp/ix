import logging
from functools import cached_property

from langchain.callbacks.manager import CallbackManager

from ix.chat.models import Chat
from ix.commands import CommandRegistry
from ix.task_log.models import Task

logger = logging.getLogger(__name__)


class IxCallbackManager(CallbackManager):
    """
    Custom callback manager that adds iX functionality.
    """

    stack_id: str
    task: Task
    command_registry: CommandRegistry

    def __init__(
        self,
        task: Task,
        stack_id: str = None,
        parent: "IxCallbackHandler" = None,  # noqa: F821
    ):
        super().__init__(handlers=[])

        self.task = task
        self.stack_id = stack_id or "root"
        self.parent = parent

    def child(self, stack_id: str) -> "IxCallbackManager":
        """Return a child clone with nested stack_id"""
        child = type(self)(
            parent=self, task=self.task, stack_id=f"{self.stack_id}.{stack_id}"
        )
        child.think_msg = self.think_msg
        return child

    @property
    def task_id(self) -> str:
        return str(self.task.id)

    @property
    def agent_id(self) -> str:
        return str(self.task.agent_id)

    @property
    def user_id(self) -> str:
        # HAX: this is currently always the owner of the chat. Likely need to update
        # this in the future to be the user making the request.
        return str(self.task.user_id)

    @cached_property
    def chat_id(self) -> str:
        try:
            chat = Chat.objects.get(task=self.task)
        except Chat.DoesNotExist:
            return None
        return chat.id
