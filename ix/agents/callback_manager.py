import logging

from langchain.callbacks import CallbackManager, BaseCallbackHandler


from ix.commands import CommandRegistry
from ix.task_log.models import Task

logger = logging.getLogger(__name__)


class IxCallbackHandler(BaseCallbackHandler):
    # TODO: probably want to move think/thought logging here
    pass


class IxCallbackManager(CallbackManager):
    """
    Custom callback manager that adds iX functionality.
    """

    stack_id: str
    task: Task
    command_registry: CommandRegistry

    def __init__(self, task: Task, stack_id=None):
        # TODO: integrate ix handlers to built in callbacks.
        super().__init__(handlers=[])

        self.task = task
        self.stack_id = stack_id or "root"

    def child(self, stack_id):
        """Return a child clone with nested stack_id"""
        child = type(self)(task=self.task, stack_id=f"{self.stack_id}.{stack_id}")
        return child
