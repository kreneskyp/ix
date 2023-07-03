from langchain.tools import PubmedQueryRun, BaseTool
from langchain.utilities import PubMedAPIWrapper

from ix.chains.loaders.tools import extract_tool_kwargs
from typing import Any


def get_pubmed(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = PubMedAPIWrapper(**kwargs)
    return PubmedQueryRun(api_wrapper=wrapper, **tool_kwargs)
