import logging
from typing import Dict, Any

from ix.chains.loaders.context import IxContext
from langchain import PromptTemplate
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    BaseStringMessagePromptTemplate,
)

from ix.chains.models import ChainNode

logger = logging.getLogger(__name__)


TEMPLATE_CLASSES = {
    "system": SystemMessagePromptTemplate,
    "user": HumanMessagePromptTemplate,
    "assistant": AIMessagePromptTemplate,
}


def load_prompt(node: ChainNode, context: IxContext) -> Dict[str, Any]:
    """
    Loading helper for Langchain prompt template classes
    """
    loader = {
        "langchain.prompts.chat.ChatPromptTemplate": load_chat_prompt,
    }[node.class_path]
    return loader(node)


def load_chat_prompt(node: ChainNode) -> Dict[str, Any]:
    """
    Load a ChatPromptTemplate from a config of messages
    """
    config = node.config.copy()

    # load message templates and build prompt
    messages = []
    input_variables = set()
    for message in config.pop("messages"):
        message_instance = create_message(message)
        messages.append(message_instance)
        input_variables.update(message_instance.input_variables)

    config["messages"] = messages
    config["input_variables"] = input_variables
    return config


def create_message(message: Dict[str, Any]) -> BaseStringMessagePromptTemplate:
    """Create a message template"""
    message_config = message.copy()
    template_class = TEMPLATE_CLASSES[message_config.pop("role")]
    prompt_config = {
        "input_variables": [],
        "partial_variables": {},
    }
    prompt_config.update(message_config)
    prompt = PromptTemplate(**prompt_config)
    return template_class(prompt=prompt)
