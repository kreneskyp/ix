import logging
from functools import singledispatch
from typing import Dict, Any, Union, Type, Tuple, List

from langchain.memory import CombinedMemory
from langchain.schema import BaseMemory, BaseChatMessageHistory
from pydantic import BaseModel

from ix.agents.callback_manager import IxCallbackManager
from ix.chains.loaders.core import load_node
from ix.chains.models import ChainNode
from ix.utils.importlib import import_class


logger = logging.getLogger(__name__)


# config options for memory classes that do not have Ix specific options
MEMORY_CLASSES = {}


def get_memory_option(cls: Type[BaseModel], name: str, default: Any):
    """Get a memory config value from a class or default"""
    if issubclass(cls, BaseModel) and name in cls.__fields__:
        # support for pydantic models
        return cls.__fields__[name].default
    elif hasattr(cls, name):
        # support for regular classes
        return getattr(cls, name)
    elif cls in MEMORY_CLASSES:
        # fallback to separate config
        return MEMORY_CLASSES[cls].get(name, default)
    return default


@singledispatch
def load_memory_config(
    node: ChainNode,
    callback_manager: IxCallbackManager,
) -> BaseMemory:
    """Load a memory instance using a config"""
    memory_class = import_class(node.class_path)
    logger.debug(f"loading memory class={node.class_path} node={node.id}")
    memory_config = node.config.copy() if node.config else {}

    # load session_id if scope is supported
    if get_memory_option(memory_class, "supports_session", False):
        session_id, session_id_key = get_memory_session(
            memory_config, callback_manager, memory_class
        )
        memory_config[session_id_key] = session_id

    return memory_config


def load_chat_memory_backend_config(
    node: ChainNode, callback_manager: IxCallbackManager
):
    backend_class = import_class(node.class_path)
    logger.debug(f"loading BaseChatMessageHistory class={backend_class} config={node}")
    backend_config = node.config.copy()

    # always add scope to chat message backend
    session_id, session_id_key = get_memory_session(
        backend_config, callback_manager, backend_class
    )
    logger.debug(
        f"load_chat_memory_backend session_id={session_id} session_id_key={session_id_key}"
    )
    backend_config[session_id_key] = session_id

    return backend_config


def load_memory_property(
    node_group: List[ChainNode], callback_manager: IxCallbackManager
) -> BaseMemory:
    """
    Load memories from a list of configs and merge in to a CombinedMemory instance.
    """
    logger.debug(f"Combining memory classes config={node_group}")

    if len(node_group) == 1:
        # no need to combine
        return load_node(node_group[0], callback_manager)

    # auto-merge into CombinedMemory
    return CombinedMemory(
        memories=[load_node(node, callback_manager) for node in node_group]
    )


def get_memory_session(
    config: Dict[str, Any],
    callback_manager: IxCallbackManager,
    cls: Union[BaseMemory, BaseChatMessageHistory],
) -> Tuple[str, str]:
    """
    Parse the session scope from the given configuration and callback manager.

    This function retrieves the scope from the configuration, verifies if the scope
    is supported by the given class (cls), and then fetches the corresponding identifier
    from the callback manager based on the scope. It then constructs the session id
    by appending the session id base, scope, and scope id.

    Parameters:
    - config (Dict[str, Any]): The configuration dictionary. Config options include:
      * "scope" (str): The scope of the interaction. Supported scopes are: "chat", "agent", "task", and "user".
      * "prefix" (str): The base string for the session id. Default is an empty string.
      * "key" (str): The key name for the session id in the return tuple. Default is "session_id".

    - callback_manager (IxCallbackManager): The callback manager object which stores identifiers
      for different scopes.

    - cls (Union[BaseMemory, BaseChatMessageHistory]): Class object that supports the required scope.

    Returns:
    - Tuple[str, str]: A tuple containing the session id and session id key.

    Raises:
    - ValueError: If the given scope is not recognized.

    Example:
    config = {
      "scope": "chat",
      "prefix": "prefix_unique_to_chat_scope",
      "key": "session_id"
    }
    session_id, session_id_key = get_memory_session(config, callback_manager, BaseChatMessageHistory)
    """

    # fetch scope
    scope = config.pop("session_scope", "chat")
    if scope in {"", None}:
        scope = "chat"
    supported_scopes = get_memory_option(cls, "supported_scopes", False)
    if supported_scopes:
        assert scope in supported_scopes

    # load session_id from context based on scope
    if scope == "chat":
        scope_id = callback_manager.chat_id
    elif scope == "agent":
        scope_id = callback_manager.agent_id
    elif scope == "task":
        scope_id = callback_manager.task_id
    elif scope == "user":
        scope_id = callback_manager.user_id
    else:
        raise ValueError(f"unknown scope={scope}")

    # build session_id
    prefix = config.pop("session_prefix", None)
    if prefix:
        session_id = f"{prefix}_{scope}_{scope_id}"
    else:
        session_id = f"{scope}_{scope_id}"

    key = config.pop("session_key", "session_id")
    return session_id, key
