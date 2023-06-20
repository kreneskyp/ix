import logging
from typing import Any, List

from langchain import LLMChain as LangchainLLMChain
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
)

from ix.task_log.models import TaskLogMessage

logger = logging.getLogger(__name__)

TEMPLATE_CLASSES = {
    "system": SystemMessagePromptTemplate,
    "user": HumanMessagePromptTemplate,
    "assistant": AIMessagePromptTemplate,
}


class LLMChain(LangchainLLMChain):
    """Wrapper around LLMChain to provide from_config initialization"""

    @property
    def input_keys(self) -> List[str]:
        """
        Overridden to filter out memory variables from input_variables.
        This is to be compatible with Sequence, which will raise a validation
        error since it does not detect the variable is from memory.
        """
        as_set = set(self.prompt.input_variables)
        if self.memory:
            as_set -= set(self.memory.memory_variables)
        return list(as_set)


class LLMReply(LLMChain):
    """
    Wrapper around LLMChain that records output as an ASSISTANT message.
    This simplifies making simple agents that just reply to messages.
    """

    def run(self, *args, **kwargs) -> Any:
        response = super().run(*args, **kwargs)
        TaskLogMessage.objects.create(
            task_id=self.callbacks.task.id,
            role="assistant",
            parent=self.callbacks.think_msg,
            content={
                "type": "ASSISTANT",
                "text": response,
                # "agent": str(self.callback_manager.task.agent.id),
                "agent": self.callbacks.task.agent.alias,
            },
        )

        return response
