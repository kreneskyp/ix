from typing import Any

from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.utils import Input, Output


class IXChatOpenAI(ChatOpenAI):
    def bind(self, **kwargs: Any) -> Runnable[Input, Output]:
        """
        Overridden to map function_call to the spec format. Requires a custom
        component but keeps the binding interface consistent.
        """

        if "function_call" in kwargs:
            kwargs = kwargs.copy()
            if isinstance(kwargs["function_call"], str):
                kwargs["function_call"] = {"name": kwargs["function_call"]}

        return super().bind(**kwargs)
