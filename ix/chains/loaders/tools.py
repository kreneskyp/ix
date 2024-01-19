from typing import List, Type

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.schema.runnable import Runnable
from langchain.tools import BaseTool, Tool
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from pydantic.v1 import BaseModel as BaseModelV1

from ix.chains.fixture_src.tools import TOOL_BASE_FIELDS
from ix.chains.loaders.context import IxContext
from ix.chains.loaders.core import init_flow
from ix.chains.models import ChainEdge
from ix.runnable.ix import IxNode

TOOL_BASE_FIELD_NAMES = {tool["name"] for tool in TOOL_BASE_FIELDS}


def extract_tool_kwargs(kwargs: dict) -> dict:
    """
    Extract tool kwargs from kwargs.
    """
    tool_kwargs = {}
    for key, value in list(kwargs.items()):
        if key in TOOL_BASE_FIELD_NAMES:
            tool_kwargs[key] = kwargs.pop(key)
    return tool_kwargs


def load_flow_property(
    edge_group: List[ChainEdge], context: IxContext
) -> List[Runnable]:
    nodes = [edge.source for edge in edge_group]
    flows = init_flow(nodes, context)

    if not isinstance(flows, list):
        flows = [flows]

    return flows


class StructuredToolV2(StructuredTool):
    """Extension of StructuredTool that supports Pydantic v2 schemas.

    The LangChain version requires v1 models but the dynamic models are v2 models.
    Fix this whenever upstream is updated to use v2.
    """

    args_schema: Type[BaseModel] = Field(..., description="The tool schema.")


def get_runnable_tool(
    name: str, description: str, runnable: Runnable
) -> StructuredTool:
    """Create a StructuredTool from a Runnable.

    Requires a Runnable that has an input_schema matching the args required to
    run the Runnable.
    """

    def invoke_shim(*args, **kwargs):
        return runnable.invoke(input=kwargs)

    async def ainvoke_shim(*args, **kwargs):
        return await runnable.ainvoke(input=kwargs)

    # Support Runnable that use Pydantic v1 & v2 to define schemas
    if issubclass(runnable.input_schema, BaseModel):
        tool_class = StructuredToolV2
    elif issubclass(runnable.input_schema, BaseModelV1):
        tool_class = StructuredTool
    else:
        raise ValueError(
            f"Unsupported input schema type {runnable.input_schema.__class__}"
        )

    return tool_class(
        name=name,
        description=description,
        func=invoke_shim,
        coroutine=ainvoke_shim,
        args_schema=runnable.input_schema,
    )


def load_tool_property(
    edge_group: List[ChainEdge], context: IxContext, **kwargs
) -> BaseTool:
    """Loads all connected nodes as Tools. Intended for old style
    agents that still expect BaseTool instances.
    """
    flows = load_flow_property(edge_group, context)
    tools = []

    for root in flows:
        # handle single node
        if isinstance(root, IxNode):
            child = root.child

            # unpack Tools & Toolkits for agents
            if isinstance(child, BaseTool):
                tools.append(child)
                continue
            elif isinstance(child, BaseToolkit):
                tools.extend(child.get_tools())
                continue
            elif isinstance(child, Runnable):
                tools.append(
                    get_runnable_tool(
                        name=root.name, description=root.description, runnable=child
                    )
                )
                continue
            else:
                raise ValueError(f"Unsupported tool child type {child.__class__}")

        # unpack Tools & Toolkits for agents
        elif isinstance(root, BaseTool):
            tools.append(root)
            continue
        elif isinstance(root, BaseToolkit):
            tools.extend(root.get_tools())
            continue

        # runnables as tool: chains, agents, retrievers, etc.
        elif isinstance(root, Runnable):
            tools.append(
                Tool(
                    name=root.name,
                    description=root.description,
                    runnable=root,
                    func=root.invoke,
                    coroutine=root.ainvoke,
                    args_schema=root.input_schema,
                )
            )

        raise ValueError(f"Unsupported tool type {root.__class__}")
    return tools
