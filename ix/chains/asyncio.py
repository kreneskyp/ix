from typing import Optional, Any, Dict
from asgiref.sync import sync_to_async
from langchain.callbacks.manager import (
    CallbackManagerForChainRun,
)


class SyncToAsyncRun:
    """
    Mixin to convert a chain or tool to run asynchronously by using
    sync_to_async to convert the run method to a coroutine.

    This doesn't provide full async support, but it does allow for
    the chain/tool to work.
    """

    async def _arun(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Use the tool asynchronously."""
        result = await sync_to_async(self._run)(*args, **kwargs)
        return result


class SyncToAsyncCall:
    """
    Mixin to convert a chain or tool to run asynchronously by using
    sync_to_async to convert the _call method to a coroutine.

    This doesn't provide full async support, but it does allow for
    the chain/tool to work.
    """

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        result = await sync_to_async(self._call)(inputs, run_manager=run_manager)
        return result
