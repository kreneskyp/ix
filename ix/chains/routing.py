import logging
from typing import Dict, Any, List

from jsonpath_ng import parse as jsonpath_parse
from langchain.chains import SequentialChain
from langchain.chains.base import Chain
from langchain.schema import BaseLanguageModel

from ix.agents.callback_manager import IxCallbackManager
from ix.agents.llm import load_chain


logger = logging.getLogger(__name__)


class IXSequence(SequentialChain):
    """Wrapper around SequentialChain to provide from_config initialization"""

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


class MapSubchain(Chain):
    """
    Chain that runs a subchain for each element in a list input

    List input is read from inputs using jsonpath set as `map_input` and mapped as
    input_variable `map_input_to`. `map_input_to` is automatically added to input_variables
    if not already present.

    Each iteration will receive the outputs of the previous iteration under the key `outputs`

    Results are output as a list under `output_key`
    """

    chain: Chain
    input_variables: List[str]
    map_input: str
    map_input_to: str
    output_key: str

    @property
    def _chain_type(self) -> str:
        return "ix.MapSubchain"  # pragma: no cover

    @property
    def input_keys(self) -> List[str]:
        return self.input_variables

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    async def _acall(self, inputs: Dict[str, str]) -> Dict[str, str]:
        pass  # pragma: no cover

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        map_input = self.map_input
        map_input_to = self.map_input_to

        # map input to values list
        logger.debug(
            f"MapSubchain mapping values from map_input={map_input} to map_input_to={map_input_to}"
        )
        jsonpath_expr = jsonpath_parse(map_input)
        json_matches = jsonpath_expr.find(inputs)
        values = json_matches[0].value
        chain_inputs = inputs.copy()
        logger.debug(f"MapSubchain mapped values={values}")

        # run chain for each value
        outputs = []
        for value in values:
            logger.debug(f"MapSubchain processing value={value}")
            iteration_inputs = chain_inputs.copy()
            iteration_inputs[map_input_to] = value
            logger.debug(f"MapSubchain iteration_inputs={iteration_inputs}")
            iteration_outputs = self.chain.run(outputs=outputs, **iteration_inputs)
            logger.error(iteration_outputs)
            iteration_mapped_output = iteration_outputs
            logger.debug(f"MapSubchain response outputs={iteration_mapped_output}")
            outputs.append(iteration_mapped_output)

        # return as output_key
        return {self.output_key: outputs}

    @classmethod
    def from_config(
        cls, config: Dict[str, Any], callback_manager: "IxCallbackManager"
    ) -> "MapSubchain":
        logger.debug(f"Loading MapSubchain config={config}")

        map_input_to = config["map_input_to"]

        # create copy of input_variables
        input_variables = list(config.get("input_variables", []))

        # load chains into an IXSequence to simplify setup
        chain_config = {
            "chains": config.pop("chains"),
            "input_variables": input_variables,
        }

        if map_input_to not in chain_config["input_variables"]:
            chain_config["input_variables"].append(map_input_to)

        chain = IXSequence.from_config(chain_config, callback_manager=callback_manager)

        # build instance
        return cls(**config, chain=chain)
