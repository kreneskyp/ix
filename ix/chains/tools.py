from langchain.chains.base import Chain
from langchain.tools import Tool, BaseTool


def chain_as_tool(chain: Chain, name: str, description: str, **kwargs) -> BaseTool:
    """Converts a chain into a tool."""
    return Tool(
        name=name,
        description=description,
        func=chain.invoke,
        coroutine=chain.ainvoke,
        **kwargs
    )
