from asgiref.sync import sync_to_async
from langchain import WolframAlphaAPIWrapper
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun
from langchain.tools import BaseTool, WolframAlphaQueryRun

from ix.chains.loaders.tools import extract_tool_kwargs
from typing import Any, Optional


class AsyncWolframAlphaQueryRun(WolframAlphaQueryRun):
    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        result = await sync_to_async(self._run)(query, run_manager=run_manager)
        return result


def get_wolfram_alpha(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = WolframAlphaAPIWrapper(**kwargs)
    return AsyncWolframAlphaQueryRun(api_wrapper=wrapper, **tool_kwargs)
