from ix.chains.asyncio import SyncToAsyncRun
from ix.chains.loaders.tools import extract_tool_kwargs
from typing import Any

from langchain import GoogleSerperAPIWrapper, GoogleSearchAPIWrapper
from langchain.tools import (
    BaseTool,
    GoogleSearchResults,
    GoogleSerperRun,
    GoogleSerperResults,
)


def get_google_serper(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = GoogleSerperAPIWrapper(**kwargs)
    return GoogleSerperRun(api_wrapper=wrapper, **tool_kwargs)


def get_google_serper_results_json(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = GoogleSerperAPIWrapper(**kwargs)
    return GoogleSerperResults(api_wrapper=wrapper, **tool_kwargs)


class AsyncGoogleSearchResults(SyncToAsyncRun, GoogleSearchResults):
    pass


def get_google_search(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = GoogleSearchAPIWrapper(**kwargs)
    return AsyncGoogleSearchResults(
        api_wrapper=wrapper, name="google_search", **tool_kwargs
    )


def get_google_search_results_json(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = GoogleSearchAPIWrapper(**kwargs)
    return AsyncGoogleSearchResults(
        api_wrapper=wrapper, name="google_search", **tool_kwargs
    )
