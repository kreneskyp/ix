from asgiref.sync import sync_to_async
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun

from ix.chains.loaders.tools import extract_tool_kwargs
from typing import Any, Optional

from langchain import GoogleSerperAPIWrapper, GoogleSearchAPIWrapper, SerpAPIWrapper
from langchain.tools import (
    BaseTool,
    Tool,
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


class AsyncGoogleSearchResults(GoogleSearchResults):
    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        result = await sync_to_async(self._run)(query, run_manager=run_manager)
        return result


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


def get_serpapi(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    return Tool(
        name="Search",
        description="A search engine. Useful for when you need to answer questions "
        "about current events. Input should be a search query.",
        func=SerpAPIWrapper(**kwargs).run,
        coroutine=SerpAPIWrapper(**kwargs).arun,
        **tool_kwargs
    )
