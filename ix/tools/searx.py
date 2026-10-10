from langchain import SearxSearchWrapper
from langchain.tools import BaseTool, SearxSearchResults, SearxSearchRun

from ix.chains.loaders.tools import extract_tool_kwargs


def get_searx_search(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = SearxSearchWrapper(**kwargs)
    return SearxSearchRun(wrapper=wrapper, **tool_kwargs)


def get_searx_search_results_json(**kwargs) -> BaseTool:
    wrapper_kwargs = {k: v for k, v in kwargs.items() if k != "num_results"}
    tool_kwargs = extract_tool_kwargs(wrapper_kwargs)
    wrapper = SearxSearchWrapper(**wrapper_kwargs)
    return SearxSearchResults(wrapper=wrapper, **tool_kwargs)
