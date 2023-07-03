from langchain import WikipediaAPIWrapper
from langchain.tools import WikipediaQueryRun, BaseTool

from ix.chains.loaders.tools import extract_tool_kwargs
from typing import Any


def get_wikipedia(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = WikipediaAPIWrapper(**kwargs)
    return WikipediaQueryRun(api_wrapper=wrapper, **tool_kwargs)
