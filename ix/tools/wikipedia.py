from typing import Any
from langchain import WikipediaAPIWrapper
from langchain.tools import WikipediaQueryRun, BaseTool

from ix.chains.asyncio import SyncToAsync
from ix.chains.loaders.tools import extract_tool_kwargs


class AsyncWikipediaQueryRun(SyncToAsync, WikipediaQueryRun):
    pass


def get_wikipedia(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = WikipediaAPIWrapper(**kwargs)
    return AsyncWikipediaQueryRun(api_wrapper=wrapper, **tool_kwargs)
