from dataclasses import dataclass
from functools import cached_property

from django.db.models import Q

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
        try:
            chat = Chat.objects.get(Q(task=self.task) | Q(task_id=self.task.parent_id))
        except Chat.DoesNotExist:
            return None
        return chat.id
