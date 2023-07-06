from langchain import ArxivAPIWrapper
from langchain.tools import BaseTool, ArxivQueryRun

from ix.chains.asyncio import SyncToAsync
from ix.chains.loaders.tools import extract_tool_kwargs
from typing import Any


class AsyncArxivQueryRun(SyncToAsync, ArxivQueryRun):
    pass


def get_arxiv(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = ArxivAPIWrapper(**kwargs)
    return AsyncArxivQueryRun(api_wrapper=wrapper, **tool_kwargs)
