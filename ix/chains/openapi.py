import logging
from unittest import mock

from langchain.chains import SequentialChain
from langchain.chains.openai_functions.openapi import (
    get_openapi_chain,
    SimpleRequestChain,
)
from langchain.prompts import ChatPromptTemplate

from ix.chains.asyncio import SyncToAsyncCall

logger = logging.getLogger(__name__)


class AsyncSimpleRequestChainRun(SyncToAsyncCall, SimpleRequestChain):
    pass


def get_openapi_chain_async(**kwargs) -> SequentialChain:
    """
    Extremely hacky way of injecting asyncio support into LangChain's function.
    Done within this wrapper function to limit the scope of the patch.
    """
    with mock.patch(
        "langchain.chains.openai_functions.openapi.SimpleRequestChain",
        new=AsyncSimpleRequestChainRun,
    ):
        # modified to use `user_input` for consistency with other chains
        if "prompt" not in kwargs:
            kwargs["prompt"] = ChatPromptTemplate.from_template(
                "Use the provided API's to respond to this user query:\n\n{user_input}"
            )

        chain = get_openapi_chain(**kwargs)
        return chain
