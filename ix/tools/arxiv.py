from langchain import ArxivAPIWrapper
from langchain.tools import BaseTool, ArxivQueryRun

from ix.chains.loaders.tools import extract_tool_kwargs
from typing import Any


def get_arxiv(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = ArxivAPIWrapper(**kwargs)
    return ArxivQueryRun(api_wrapper=wrapper, **tool_kwargs)
