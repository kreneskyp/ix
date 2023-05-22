import logging
from typing import Dict, Any, Tuple

from langchain.prompts.chat import BaseStringMessagePromptTemplate

from ix.agents.callback_manager import IxCallbackManager
from ix.chains.llm_chain import LLMChain
from ix.commands import CommandRegistry


logger = logging.getLogger(__name__)


class LLMToolChain(LLMChain):
    """
    LLMChain that loads tools from the ToolRegistry and adds them as a partial_variables.
    to messages. The set of tools can be configured by setting `tools` in the config.
    """

    @staticmethod
    def create_message(
        message: Dict[str, Any], config, context: Dict[str, Any]
    ) -> BaseStringMessagePromptTemplate:
        """Extend to load tools to partial variables"""
        message_config = message.copy()
        partial_variables = message_config.get("partial_variables", {})
        if "{tools}" in message_config["template"] and "tools" not in partial_variables:
            tool_registry = CommandRegistry.for_tools(context["tools"])
            tools_prompt = tool_registry.command_prompt()
            partial_variables["tools"] = tools_prompt
        message_config["partial_variables"] = partial_variables
        return LLMChain.create_message(message_config, config, context)

    @staticmethod
    def prepare_config(
        config: Dict[str, Any], callback_manager: IxCallbackManager
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Prepare config by moving tools to context"""
        tools_config = config.pop("tools", [])
        config, context = LLMChain.prepare_config(config, callback_manager)
        context["tools"] = tools_config
        return config, context
