from asgiref.sync import sync_to_async
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun
from langchain.tools import PubmedQueryRun, BaseTool
from langchain.utilities import PubMedAPIWrapper

from ix.chains.loaders.tools import extract_tool_kwargs
from typing import Any, Optional


class AsyncPubmedQueryRun(PubmedQueryRun):
    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        result = await sync_to_async(self._run)(query, run_manager=run_manager)
        return result


def get_pubmed(**kwargs: Any) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = PubMedAPIWrapper(**kwargs)
    return AsyncPubmedQueryRun(api_wrapper=wrapper, **tool_kwargs)
