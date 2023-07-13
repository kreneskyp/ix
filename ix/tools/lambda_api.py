from asgiref.sync import sync_to_async
from langchain.tools import BaseTool, Tool
from langchain.utilities import LambdaWrapper

from ix.chains.loaders.tools import extract_tool_kwargs
from typing import Any


def get_lambda_api(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = LambdaWrapper(**kwargs)
    return Tool(
        name=kwargs["awslambda_tool_name"],
        description=kwargs["awslambda_tool_description"],
        func=wrapper.run,
        coroutine=sync_to_async(wrapper.run),
        **tool_kwargs
    )
