import sys
from typing import Callable

from langchain.prompts import MessagesPlaceholder

from langchain.agents import AgentType, AgentExecutor
from langchain.agents import initialize_agent as initialize_agent_base
from langchain.chains.base import Chain


def initialize_agent(agent: AgentType, **kwargs) -> Chain:
    """
    Extended version of the initialize_agent function from ix.chains.agents.

    Modifications:
    - unpacks agent_kwargs: allows agent_kwargs to be flattened into the ChainNode config
      A flattened config simplifies the UX integration such that it works with TypeAutoFields
    """
    # Re-pack agent_kwargs__* arguments into agent_kwargs
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    }

    # Inject placeholders into prompt for memory if provided
    if memories := kwargs.get("memory", None):
        if not isinstance(memories, list):
            memories = [memories]
        placeholders = []
        for component in memories:
            if not hasattr(component, "memory_key"):
                raise ValueError(
                    f"Memory component {component} does not have a memory_key attribute."
                )
            if getattr(component, "return_messages", False):
                raise ValueError(
                    f"Memory component {component} has return_messages=True. Agents require "
                    f"return_messages=False."
                )
            placeholders.append(MessagesPlaceholder(variable_name=component.memory_key))

    for key, value in kwargs.items():
        if key.startswith("agent_kwargs__"):
            agent_kwargs[key[15:]] = value
            del kwargs[key]
    kwargs["agent_kwargs"] = agent_kwargs

    return initialize_agent_base(agent=agent, **kwargs)


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
