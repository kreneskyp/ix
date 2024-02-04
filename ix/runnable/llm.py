from typing import Any

from langchain.schema.runnable import Runnable
from langchain.schema.runnable.utils import Input, Output
from langchain_community.chat_models import ChatOpenAI

from ix.data.types import Schema


def to_openai_fn(obj: Any) -> dict:
    if isinstance(obj, Schema):
        # HAX: include the schema description in the function description to ensure
        # it's available to the LLM to use the function.
        schema_description = obj.value.get("description", "")

        return {
            "name": obj.name,
            "description": f"{obj.description}\n\n{schema_description}",
            "parameters": obj.value,
        }
    else:
        return obj


class IXChatOpenAI(ChatOpenAI):
    def bind(self, **kwargs: Any) -> Runnable[Input, Output]:
        """
        Overridden to:
        - map function_call to the spec format. Requires a custom
           component but keeps the binding interface consistent.
        - convert functions as IX Schemas into OpenAI function specs
        """
        kwargs = kwargs.copy()

        if "function_call" in kwargs:
            if isinstance(kwargs["function_call"], str):
                kwargs["function_call"] = {"name": kwargs["function_call"]}

        if "functions" in kwargs:
            kwargs["functions"] = [to_openai_fn(obj) for obj in kwargs["functions"]]

        return super().bind(**kwargs)
