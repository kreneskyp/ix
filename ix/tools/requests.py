from langchain.requests import TextRequestsWrapper
from langchain.tools import (
    BaseTool,
    RequestsDeleteTool,
    RequestsPutTool,
    RequestsPatchTool,
    RequestsPostTool,
    RequestsGetTool,
)

from ix.chains.loaders.tools import extract_tool_kwargs


def get_tools_requests_get(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = TextRequestsWrapper(**kwargs)
    return RequestsGetTool(requests_wrapper=wrapper, **tool_kwargs)


def get_tools_requests_post(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = TextRequestsWrapper(**kwargs)
    return RequestsPostTool(requests_wrapper=wrapper, **tool_kwargs)


def get_tools_requests_patch(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = TextRequestsWrapper(**kwargs)
    return RequestsPatchTool(requests_wrapper=wrapper, **tool_kwargs)


def get_tools_requests_put(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = TextRequestsWrapper(**kwargs)
    return RequestsPutTool(requests_wrapper=wrapper, **tool_kwargs)


def get_tools_requests_delete(**kwargs) -> BaseTool:
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = TextRequestsWrapper(**kwargs)
    return RequestsDeleteTool(requests_wrapper=wrapper, **tool_kwargs)
