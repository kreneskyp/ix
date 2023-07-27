from typing import Any
from langchain.utilities import MetaphorSearchAPIWrapper
from langchain.tools import MetaphorSearchResults
from langchain.tools import BaseTool, MetaphorSearchResults  # metaphorQueryRun

from ix.chains.asyncio import SyncToAsyncRun
from ix.chains.loaders.tools import extract_tool_kwargs


class AsyncMetaphorQueryRun(SyncToAsyncRun, MetaphorSearchResults):
    pass


def get_metaphor(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = MetaphorSearchAPIWrapper(**kwargs)
    # metaphor_tool = MetaphorSearchResults(api_wrapper=search)
    return AsyncMetaphorQueryRun(api_wrapper=wrapper, **tool_kwargs)
