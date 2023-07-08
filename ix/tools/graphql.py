from langchain.tools import BaseTool, BaseGraphQLTool
from langchain.utilities import GraphQLAPIWrapper

from ix.chains.asyncio import SyncToAsyncRun
from ix.chains.loaders.tools import extract_tool_kwargs


class AsyncGraphQLTool(SyncToAsyncRun, BaseGraphQLTool):
    pass


def get_graphql_tool(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = GraphQLAPIWrapper(graphql_endpoint=kwargs["graphql_endpoint"])
    return AsyncGraphQLTool(graphql_wrapper=wrapper, **tool_kwargs)
