from typing import Optional, Any, AsyncIterator

from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.utils import Input, Output


class StreamableTransform:
    """
    Mixin to make a runnable that proxies streaming to it's transform method.
    """

    async def astream(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[Output]:
        """proxy to atransform"""

        async def input_aiter() -> AsyncIterator[Input]:
            yield input

        async for chunk in self.atransform(input_aiter(), config, **kwargs):
            yield chunk
