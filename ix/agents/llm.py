import logging
from typing import Dict, Any, Union
from langchain.schema import BaseLanguageModel

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


def load_chain(config: Dict[str, Any], callback_manager: IxCallbackManager):
    chain_class = import_class(config["class_path"])
    logger.debug(f"loading chain config={config}")
    instance = chain_class.from_config(
        config.get("config", {}), callback_manager=callback_manager
    )
    return instance
