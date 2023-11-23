from typing import List

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.schema.runnable import Runnable
from langchain.tools import BaseTool, Tool

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
