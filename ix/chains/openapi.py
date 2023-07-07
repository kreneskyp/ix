import logging
from unittest import mock
from langchain.chains.openai_functions.openapi import (
    get_openapi_chain,
    SimpleRequestChain,
)
from ix.chains.asyncio import SyncToAsyncCall

logger = logging.getLogger(__name__)


class AsyncSimpleRequestChainRun(SyncToAsyncCall, SimpleRequestChain):
    pass


def get_openapi_chain_async(**kwargs):
    """
    Extremely hacky way of injecting asyncio support into LangChain's function.
    Done within this wrapper function to limit the scope of the patch.
    """
    with mock.patch(
        "langchain.chains.openai_functions.openapi.SimpleRequestChain",
        new=AsyncSimpleRequestChainRun,
    ):
        chain = get_openapi_chain(**kwargs)
        return chain
