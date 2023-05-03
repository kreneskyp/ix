import logging

from langchain.callbacks import CallbackManager

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
        self, task: Task, stack_id: str = None, parent: "IxCallbackHandler" = None
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
        return child
