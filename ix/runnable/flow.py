from typing import Any, List, Optional, Dict
from uuid import UUID

from langchain.callbacks.manager import (
    CallbackManagerForChainRun,
    AsyncCallbackManagerForChainRun,
)
from langchain.schema.runnable import (
    RunnableSerializable,
    RunnableConfig,
    patch_config,
    RunnableParallel,
)
from langchain.schema.runnable.utils import Input, Output
from langchain_core.runnables import Runnable

from ix.chains.loaders.context import IxContext
from ix.chains.models import Chain as ChainModel


def load_chain_id(
    chain_id: UUID, context: IxContext, **kwargs
) -> Runnable[Input, Output]:
    """Load a Runnable from a chain_id.

    This initializer is used by the Reference component to transform
    the config (chain_id) into the component it refers to. The component's
    Runnable is returned directly.
    """
    chain_obj = ChainModel.objects.get(id=chain_id)
    return chain_obj.load_chain(context=context)


def load_agent_id(
    chain_id: UUID, context: IxContext, **kwargs
) -> Runnable[Input, Output]:
    """Load an agent Runnable from a chain_id. Proxy to load_chain_id."""
    return load_chain_id(chain_id, context, **kwargs)


class RunnableEachSequential(RunnableSerializable[List[Input], List[Output]]):
    """Runs a flow for each item in a list sequentially."""

    workflow: RunnableSerializable[Input, Output]

    def _invoke(
        self,
        inputs: List[Input],
        run_manager: CallbackManagerForChainRun,
        config: RunnableConfig,
        **kwargs: Any,
    ) -> List[Output]:
        results = []
        for item in inputs:
            result = self.workflow.invoke(
                item, patch_config(config, callbacks=run_manager.get_child()), **kwargs
            )
            result.append(result)
        return results

    def invoke(
        self, input: List[Input], config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> List[Output]:
        return self._call_with_config(self._invoke, input, config, **kwargs)

    async def _ainvoke(
        self,
        inputs: List[Input],
        run_manager: AsyncCallbackManagerForChainRun,
        config: RunnableConfig,
        **kwargs: Any,
    ) -> List[Output]:
        results = []
        for item in inputs:
            result = await self.workflow.ainvoke(
                item, patch_config(config, callbacks=run_manager.get_child()), **kwargs
            )
            result.append(result)
        return results

    async def ainvoke(
        self, input: List[Input], config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> List[Output]:
        return await self._acall_with_config(self._ainvoke, input, config, **kwargs)


class MergeList(RunnableSerializable[Input, Output | List[Output]]):
    """Merge values into a list."""

    steps: List[RunnableSerializable[Input, Output]]
    """Steps to run and merge into a single list."""

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Is this class serializable?"""
        return True

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> List[Output]:
        runnable_map = RunnableParallel(
            **{i: step for i, step in enumerate(self.steps)}
        )
        raw_output = runnable_map.invoke(input, config, **kwargs)
        output = []
        for run in raw_output:
            if isinstance(run, list):
                output.extend(run)
            else:
                output.append(run)
        return output

    async def ainvoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> List[Output]:
        runnable_map = RunnableParallel(
            **{str(i): step for i, step in enumerate(self.steps)}
        )
        raw_output = await runnable_map.ainvoke(input, config, **kwargs)
        output = []
        for run in raw_output.values():
            if isinstance(run, list):
                output.extend(run)
            else:
                output.append(run)

        return output
