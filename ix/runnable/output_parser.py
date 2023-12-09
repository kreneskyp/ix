import json
from typing import Optional, Any

from langchain.schema import AIMessage
from langchain.schema.runnable import RunnableSerializable, RunnableConfig
from pydantic import BaseModel


class FunctionCall(BaseModel):
    name: str
    arguments: dict[str, Any]


class ParseFunctionCall(RunnableSerializable[AIMessage, FunctionCall]):
    """
    Parse OpenAI function call from an AI Message. Used in conjunction with
    functions bound to the LLM request.
    """

    def invoke(
        self,
        input: AIMessage,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> FunctionCall:
        additional_kwargs = input.additional_kwargs
        if "function_call" in additional_kwargs:
            function_call = additional_kwargs["function_call"]
            if isinstance(function_call, str):
                function_call = json.loads(function_call)

            if isinstance(function_call["arguments"], str):
                function_call["arguments"] = json.loads(function_call["arguments"])

            return FunctionCall(**function_call)
        else:
            raise ValueError("No function call found in input.")

    async def ainvoke(
        self,
        input: AIMessage,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> FunctionCall:
        additional_kwargs = input.additional_kwargs
        if "function_call" in additional_kwargs:
            function_call = additional_kwargs["function_call"]
            if isinstance(function_call, str):
                function_call = json.loads(function_call)

            if isinstance(function_call["arguments"], str):
                function_call["arguments"] = json.loads(function_call["arguments"])

            return FunctionCall(**function_call)
        else:
            raise ValueError("No function call found in input.")
