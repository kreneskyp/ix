import logging
from typing import Dict, Any

from langchain.chains import SequentialChain
from langchain.schema import BaseLanguageModel

from ix.agents.callback_manager import IxCallbackManager
from ix.agents.llm import load_chain


logger = logging.getLogger(__name__)


class IXSequence(SequentialChain):
    """Chain that parses AI response content into JSON"""

    llm: BaseLanguageModel = None

    @classmethod
    def from_config(cls, config: Dict[str, Any], callback_manager: IxCallbackManager):
        """Load an instance from a config dictionary and runtime"""
        # TODO: pass on llm?
        # llm_config = config["llm"]
        # llm = load_llm(llm_config, callback_manager=callback_manager)

        chains = []
        for i, chain_config in enumerate(config.pop("chains")):
            chain_callback_manager = callback_manager.child(i)
            chain = load_chain(chain_config, callback_manager=chain_callback_manager)
            chains.append(chain)

        return cls(callback_manager=callback_manager, chains=chains, **config)
