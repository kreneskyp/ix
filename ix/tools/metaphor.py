import os
from typing import Any, Optional, Literal

from asgiref.sync import sync_to_async
from langchain.tools import Tool
from metaphor_python import Metaphor

from ix.chains.loaders.tools import extract_tool_kwargs


METAPHOR_METHODS = Literal["search", "get_contents", "find_similar"]


def get_metaphor_tool(
    method: METAPHOR_METHODS,
    description: str,
    metaphor_api_key: Optional[str] = None,
    **kwargs: Any,
) -> Tool:
    """Common logic for initializing a Metaphor client and returning a Tool object that can be used to run queries."""
    tool_kwargs = extract_tool_kwargs(kwargs)
    api_key = metaphor_api_key or os.environ.get("METAPHOR_API_KEY", None)
    assert (
        api_key is not None
    ), "Metaphor API key must be provided as metaphor_api_key or METAPHOR_API_KEY env var"

    client = Metaphor(api_key=api_key)
    func = getattr(client, method)
    return Tool(
        name=f"metaphor_{method}",
        description=description,
        func=func,
        coroutine=sync_to_async(func),
        **tool_kwargs,
    )


def get_metaphor_search(**kwargs: Any) -> Tool:
    """Initialize a Tool that wraps `Metaphor.client.search`"""
    description = (
        "Metaphor search engine searches the web for pages that match a given query."
    )
    return get_metaphor_tool("search", description, **kwargs)


def get_metaphor_contents(**kwargs: Any) -> Tool:
    """Initialize a Tool that wraps `Metaphor.client.get_contents`"""
    description = "Get the contents of pages. Pages are identified by ids returned by the search endpoint."
    return get_metaphor_tool("get_contents", description, **kwargs)


def get_metaphor_find_similar(**kwargs: Any) -> Tool:
    """Initialize a Tool that wraps `Metaphor.client.find_similar`"""
    description = "Find pages that are similar to a given URL."
    return get_metaphor_tool("find_similar", description, **kwargs)
