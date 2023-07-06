from typing import Optional

from asgiref.sync import sync_to_async
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun
from langchain.tools import DuckDuckGoSearchRun, BaseTool
from langchain.utilities import DuckDuckGoSearchAPIWrapper

from ix.chains.loaders.tools import extract_tool_kwargs


class AsyncDuckDuckGoSearchRun(DuckDuckGoSearchRun):
    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        result = await sync_to_async(self._run)(query, run_manager=run_manager)
        return result


def get_ddg_search(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = DuckDuckGoSearchAPIWrapper(**kwargs)
    return AsyncDuckDuckGoSearchRun(api_wrapper=wrapper, **tool_kwargs)
