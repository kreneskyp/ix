from langchain.tools import BaseTool, BingSearchRun
from langchain.utilities import BingSearchAPIWrapper

from ix.chains.asyncio import SyncToAsyncRun
from ix.chains.loaders.tools import extract_tool_kwargs


class AsyncBingSearchRun(SyncToAsyncRun, BingSearchRun):
    pass


def get_bing_search(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = BingSearchAPIWrapper(**kwargs)
    return AsyncBingSearchRun(api_wrapper=wrapper, **tool_kwargs)
