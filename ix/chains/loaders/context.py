from dataclasses import dataclass
from functools import cached_property

from ix.agents.models import Agent
from ix.chains.models import Chain
from ix.chat.models import Chat
from ix.task_log.models import Task


@dataclass
class IxContext:
    agent: Agent
    chain: Chain
    task: Task

    @property
    def user_id(self) -> str:
        # HAX: this is currently always the owner of the chat. Likely need to update
        # this in the future to be the user making the request.
        return str(self.task.user_id)

    @cached_property
    def chat_id(self) -> str:
        root_id = self.task.root_id if self.task.root_id else self.task.id
        try:
            chat = Chat.objects.get(task_id=root_id)
        except Chat.DoesNotExist:
            return None
        return chat.id
