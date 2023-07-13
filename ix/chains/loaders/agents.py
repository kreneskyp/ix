import logging
import sys
from typing import Callable

from langchain.agents import AgentType, AgentExecutor
from langchain.agents import initialize_agent as initialize_agent_base
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.chains.base import Chain

from ix.chains.agents import AgentReply


logger = logging.getLogger(__name__)


def initialize_agent(agent: AgentType, reply: int = True, **kwargs) -> Chain:
    """
    Extended version of the initialize_agent function from ix.chains.agents.

    Modifications:
    - unpacks agent_kwargs: allows agent_kwargs to be flattened into the ChainNode config
      A flattened config simplifies the UX integration such that it works with TypeAutoFields
    """
    # Re-pack agent_kwargs__* arguments into agent_kwargs
    agent_kwargs = {}
    for key, value in kwargs.items():
        if key.startswith("agent_kwargs__"):
            agent_kwargs[key[15:]] = value
            del kwargs[key]
    kwargs["agent_kwargs"] = agent_kwargs

    # unpack Toolkits into Tools
    if "tools" in kwargs:
        tools = kwargs["tools"]
        unpacked_tools = []
        for i, value in enumerate(tools):
            if isinstance(value, BaseToolkit):
                unpacked_tools.extend(value.get_tools())
            else:
                unpacked_tools.append(value)
        kwargs["tools"] = unpacked_tools
    tools = kwargs.get("tools", {})

    # TODO: wrap agents in AgentReply until streaming callbacks are implemented
    agent_executor = initialize_agent_base(agent=agent, **kwargs)
    return AgentReply(
        agent_executor=agent_executor,
        callback_manager=kwargs.get("callback_manager", None),
        reply=reply,
    )


def create_init_func(agent_type: AgentType) -> Callable:
    """
    This function creates a new initialization function for a given agent type. The initialization
    function is a proxy to the initialize_agent function, but it has a distinct name and can be
    imported directly from this module.

    Agent initialization functions are used so there is a distinct class_path for each agent type.
    This allows class_path to be used as an identifier for the agent type.

    Args:
        agent_type (str): The type of the agent to create an initialization function for.

    Returns:
        function: The newly created initialization function.
    """

    def init_func(**kwargs) -> AgentExecutor:
        return initialize_agent(agent=agent_type, **kwargs)

    return init_func


# list of function names that are created, used for debugging
FUNCTION_NAMES = []


def create_functions() -> None:
    """
    Generate initialization functions for each agent type and add them to this module.
    This will automatically create a new function for each agent type as LangChain
    creates them.
    """
    for agent_type in AgentType:
        # create an initialization function for this agent type
        init_func = create_init_func(agent_type)
        func_name = "initialize_" + agent_type.value.replace("-", "_")
        FUNCTION_NAMES.append(func_name)

        # add the function to the current module
        setattr(sys.modules[__name__], func_name, init_func)


# auto-run the function that creates the initialization functions
create_functions()
