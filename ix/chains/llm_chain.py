import logging
from typing import Dict, Any, Tuple

from langchain import LLMChain as LangchainLLMChain, PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    BaseStringMessagePromptTemplate,
)

from ix.agents.llm import load_llm
from ix.agents.callback_manager import IxCallbackManager
from ix.task_log.models import TaskLogMessage

logger = logging.getLogger(__name__)

TEMPLATE_CLASSES = {
    "system": SystemMessagePromptTemplate,
    "user": HumanMessagePromptTemplate,
    "assistant": AIMessagePromptTemplate,
}


class LLMChain(LangchainLLMChain):
    """Wrapper around LLMChain to provide from_config initialization"""

    @staticmethod
    def create_message(
        message: Dict[str, Any], config: Dict[str, Any], context: Dict[str, Any]
    ) -> BaseStringMessagePromptTemplate:
        """Create a message template"""
        message_config = message.copy()
        template_class = TEMPLATE_CLASSES[message_config.pop("role")]
        prompt_config = {
            "input_variables": [],
            "partial_variables": {},
        }
        prompt_config.update(message_config)
        logger.debug(f"LLMChain creating message with prompt_config={prompt_config}")
        prompt = PromptTemplate(**prompt_config)
        return template_class(prompt=prompt)

    @staticmethod
    def prepare_config(
        config: Dict[str, Any], callback_manager: IxCallbackManager
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Prepare config by initializing values in config. This method also splits
        config values into context for values that are meant to be available
        to initialization but are not part of config.
        """
        config["llm"] = load_llm(config["llm"], callback_manager)
        return config, {}

    @classmethod
    def from_config(cls, config: Dict[str, Any], callback_manager: IxCallbackManager):
        logger.debug(f"Loading IxLLMChain config={config}")

        prepared_config, context = cls.prepare_config(config, callback_manager)

        # load message templates
        messages = []
        for message in config.pop("messages"):
            messages.append(cls.create_message(message, prepared_config, context))

        # build prompt & chain
        prompt = ChatPromptTemplate.from_messages(messages)
        chain = cls(**config, prompt=prompt, verbose=True)
        chain.callback_manager = callback_manager

        return chain


class LLMReply(LLMChain):
    """
    Wrapper around LLMChain that records output as an ASSISTANT message.
    This simplifies making simple agents that just reply to messages.
    """

    def run(self, *args, **kwargs) -> Any:
        response = super().run(*args, **kwargs)
        TaskLogMessage.objects.create(
            task_id=self.callback_manager.task.id,
            role="assistant",
            content={
                "type": "ASSISTANT",
                "text": response,
                # "agent": str(self.callback_manager.task.agent.id),
                "agent": self.callback_manager.task.agent.alias,
            },
        )

        return response
