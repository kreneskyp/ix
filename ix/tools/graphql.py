from typing import Optional

from asgiref.sync import sync_to_async
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun
from langchain.tools import BaseTool, BaseGraphQLTool
from langchain.utilities import GraphQLAPIWrapper

from ix.chains.loaders.tools import extract_tool_kwargs


class AsyncGraphQLTool(BaseGraphQLTool):
    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        result = await sync_to_async(self._run)(query, run_manager=run_manager)
        return result


def get_graphql_tool(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = GraphQLAPIWrapper(graphql_endpoint=kwargs["graphql_endpoint"])
    return AsyncGraphQLTool(graphql_wrapper=wrapper, **tool_kwargs)
