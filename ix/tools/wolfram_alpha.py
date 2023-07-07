from langchain import WolframAlphaAPIWrapper
from langchain.tools import BaseTool, WolframAlphaQueryRun

from ix.chains.asyncio import SyncToAsync
from ix.chains.loaders.tools import extract_tool_kwargs
from typing import Any


class AsyncWolframAlphaQueryRun(SyncToAsync, WolframAlphaQueryRun):
    pass


def get_wolfram_alpha(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = WolframAlphaAPIWrapper(**kwargs)
    return AsyncWolframAlphaQueryRun(api_wrapper=wrapper, **tool_kwargs)
