from asgiref.sync import SyncToAsync, sync_to_async
from typing import Any, Optional
from langchain import WikipediaAPIWrapper
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun
from langchain.tools import WikipediaQueryRun, BaseTool

from ix.chains.loaders.tools import extract_tool_kwargs


class AsyncWikipediaQueryRun(SyncToAsync, WikipediaQueryRun):
    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        result = await sync_to_async(self._run)(query, run_manager=run_manager)
        return result


def get_wikipedia(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = WikipediaAPIWrapper(**kwargs)
    return AsyncWikipediaQueryRun(api_wrapper=wrapper, **tool_kwargs)
