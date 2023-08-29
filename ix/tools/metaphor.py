import os
from typing import Any, Optional

from asgiref.sync import sync_to_async
from langchain.tools import Tool
from metaphor_python import Metaphor

from ix.chains.loaders.tools import extract_tool_kwargs


def get_metaphor(metaphor_api_key: Optional[str], **kwargs: Any) -> Tool:
    """Metaphor search tool

    Initializes a Metaphor client and returns a Tool object that can be used to run queries.
    """
    tool_kwargs = extract_tool_kwargs(kwargs)
    api_key = metaphor_api_key or os.environ.get("METAPHOR_API_KEY", None)
    assert (
        api_key is not None
    ), "Metaphor API key must be provided as metaphor_api_key or METAPHOR_API_KEY env var"

    client = Metaphor(api_key=api_key)
    return Tool(
        name="metaphor_query",
        description="Metaphor Search. Searches the web for pages that match a given query.",
        func=client.search,
        coroutine=sync_to_async(client.search),
        **tool_kwargs
    )
