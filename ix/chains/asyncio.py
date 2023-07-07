from typing import Optional
from asgiref.sync import sync_to_async
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun


class SyncToAsync:
    """
    Mixin to convert a chain or tool to run asynchronously by using
    sync_to_async to convert the run method to a coroutine.

    This doesn't provide full async support, but it does allow for
    the chain/tool to work.
    """

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        result = await sync_to_async(self._run)(query, run_manager=run_manager)
        return result
