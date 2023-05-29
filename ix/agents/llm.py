import logging
from functools import singledispatch
from typing import Dict, Any, Union, Type, Tuple, List

from langchain.base_language import BaseLanguageModel
from langchain.memory import CombinedMemory
from langchain.schema import BaseMemory, BaseChatMessageHistory
from pydantic import BaseModel

from ix.agents.callback_manager import IxCallbackManager
from ix.utils.importlib import import_class


logger = logging.getLogger(__name__)


# mock point for testing
import_llm_class = import_class


def load_llm(
    config_or_llm: Union[BaseLanguageModel, Dict[str, Any]],
    callback_manager: IxCallbackManager,
) -> BaseLanguageModel:
    """Load a langchain LLM model from config"""
    if isinstance(config_or_llm, BaseLanguageModel):
        return config_or_llm

    config = config_or_llm
    llm_class = import_llm_class(config["class_path"])
    logger.debug(f"loading llm config={config}")

    llm_config = config.get("config", {})
    llm = llm_class(**llm_config)
    llm.callback_manager = callback_manager
    return llm


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
def load_memory(
    config: Union[Dict[str, Any], List[Dict[str, Any]]],
    callback_manager: IxCallbackManager,
) -> BaseMemory:
    """Load a memory instance using a config"""
    memory_class = import_class(config["class_path"])
    logger.debug(f"loading memory class={memory_class} config={config}")
    memory_config = config.get("config", {}).copy()

    # load session_id if scope is supported
    if get_memory_option(memory_class, "supports_session", False):
        session_id, session_id_key = get_memory_session(
            memory_config.pop("session", {}), callback_manager, memory_class
        )
        memory_config[session_id_key] = session_id

    # load chat memory backend when needed
    if "backend" in memory_config:
        chat_memory = load_chat_memory_backend(
            memory_config.pop("backend"), callback_manager
        )
        memory_config["chat_memory"] = chat_memory

    # load chat memory llm when needed
    if "llm" in memory_config and not isinstance(
        memory_config["llm"], BaseLanguageModel
    ):
        llm = load_llm(memory_config.pop("llm"), callback_manager)
        memory_config["llm"] = llm

    return memory_class(**memory_config)


@load_memory.register(list)
def _(config: List[Dict[str, Any]], callback_manager: IxCallbackManager) -> BaseMemory:
    """
    Load memories from a list of configs and merge in to a CombinedMemory instance.
    """
    logger.debug(f"Combining memory classes config={config}")
    # auto-merge into CombinedMemory
    return CombinedMemory(memories=[load_memory(c, callback_manager) for c in config])


def load_chat_memory_backend(config, callback_manager):
    backend_class = import_class(config["class_path"])
    logger.debug(
        f"loading BaseChatMessageHistory class={backend_class} config={config}"
    )
    backend_config = config.get("config", {}).copy()

    # always add scope to chat message backend
    if "session" in backend_config:
        session_id, session_id_key = get_memory_session(
            backend_config.pop("session"), callback_manager, backend_class
        )
        logger.debug(
            f"load_chat_memory_backend session_id={session_id} session_id_key={session_id_key}"
        )
        backend_config[session_id_key] = session_id

    return backend_class(**backend_config)


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
    scope = config.get("scope", "chat")
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
    prefix = config.get("prefix", None)
    if prefix:
        session_id = f"{prefix}_{scope}_{scope_id}"
    else:
        session_id = f"{scope}_{scope_id}"

    key = config.get("key", "session_id")
    return session_id, key


def load_chain(config: Dict[str, Any], callback_manager: IxCallbackManager):
    chain_class = import_class(config["class_path"])
    logger.debug(f"loading chain config={config}")
    instance = chain_class.from_config(
        config.get("config", {}), callback_manager=callback_manager
    )
    return instance
