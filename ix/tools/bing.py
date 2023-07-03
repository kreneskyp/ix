from langchain.tools import BaseTool, BingSearchRun
from langchain.utilities import BingSearchAPIWrapper

from ix.chains.loaders.tools import extract_tool_kwargs


def get_bing_search(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = BingSearchAPIWrapper(**kwargs)
    return BingSearchRun(api_wrapper=wrapper, **tool_kwargs)
