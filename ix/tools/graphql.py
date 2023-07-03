from langchain.tools import BaseTool, BaseGraphQLTool
from langchain.utilities import GraphQLAPIWrapper

from ix.chains.loaders.tools import extract_tool_kwargs


def get_graphql_tool(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = GraphQLAPIWrapper(graphql_endpoint=kwargs["graphql_endpoint"])
    return BaseGraphQLTool(graphql_wrapper=wrapper, **tool_kwargs)
