from langchain.tools import DuckDuckGoSearchRun, BaseTool
from langchain.utilities import DuckDuckGoSearchAPIWrapper

from ix.chains.asyncio import SyncToAsyncRun
from ix.chains.loaders.tools import extract_tool_kwargs


class AsyncDuckDuckGoSearchRun(SyncToAsyncRun, DuckDuckGoSearchRun):
    pass


def get_ddg_search(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = DuckDuckGoSearchAPIWrapper(**kwargs)
    return AsyncDuckDuckGoSearchRun(api_wrapper=wrapper, **tool_kwargs)
