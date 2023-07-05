import json
import logging
from typing import Any, List

from langchain import LLMChain as LangchainLLMChain
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
)
from langchain.tools import Tool, format_tool_to_openai_function

from ix.chains.functions import FunctionSchema
from ix.task_log.models import TaskLogMessage

logger = logging.getLogger(__name__)

TEMPLATE_CLASSES = {
    "system": SystemMessagePromptTemplate,
    "user": HumanMessagePromptTemplate,
    "assistant": AIMessagePromptTemplate,
}


class LLMChain(LangchainLLMChain):
    """
    Extension of LLMChain to provide additional functionality:

    - OpenAI functions may be connected as functions.
    - input_keys excludes memory variables so that memory may be directly attached.
    """

    # List of OpenAI functions to include in requests.
    functions: List[FunctionSchema | Tool] = None
    function_call: str = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_functions()

    def load_functions(self) -> None:
        """Load functions for OpenAI if llm is OpenAI"""
        if not isinstance(self.llm, ChatOpenAI):
            logger.error(f"llm is not ChatOpenAI, it is {type(self.llm)}")
            return

        if not self.functions:
            return

        if not isinstance(self.llm_kwargs, dict):
            self.llm_kwargs = {}

        if self.function_call:
            self.llm_kwargs["function_call"] = {"name": self.function_call}

        # convert Langchain BaseTool and BaseToolkit to OpenAI functions. FunctionSchema
        # are already OpenAI functions, we don't need to convert them.
        converted_functions = []
        for function in self.functions:
            if isinstance(function, Tool):
                converted_functions.append(format_tool_to_openai_function(function))
            if isinstance(function, BaseToolkit):
                converted_functions.extend(
                    format_tool_to_openai_function(tool_func) for tool_func in function.get_tools()
                )
            else:
                converted = function.copy()
                converted["parameters"] = json.loads(function["parameters"])
                converted_functions.append(converted)

        self.llm_kwargs["functions"] = converted_functions

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

    async def arun(self, *args, **kwargs) -> Any:
        response = await super().arun(*args, **kwargs)
        await TaskLogMessage.objects.acreate(
            task_id=self.callbacks.task.id,
            role="assistant",
            parent=self.callbacks.think_msg,
            content={
                "type": "ASSISTANT",
                "text": response,
                # "agent": str(self.callback_manager.task.agent.id),
                "agent": self.callbacks.agent.alias,
            },
        )

        return response
