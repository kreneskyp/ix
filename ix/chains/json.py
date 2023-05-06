import json
import logging
from typing import Dict, Any, List

from langchain.chains.base import Chain

from ix.agents.callback_manager import IxCallbackManager
from ix.agents.exceptions import MissingCommandMarkers


logger = logging.getLogger(__name__)


def parse_json(text: str, output_key: str) -> Dict[str, Any]:
    """Parse response into valid JSON"""
    start_marker = "###START###"
    end_marker = "###END###"
    start_index = text.find(start_marker)
    end_index = text.find(end_marker)

    if start_index == -1 or end_index == -1:
        # before raising attempt to parse the response as json
        # sometimes the AI returns responses that are still usable even without the markers
        try:
            data = json.loads(text.strip())
        except Exception:
            raise MissingCommandMarkers
    else:
        json_slice = text[start_index + len(start_marker): end_index].strip()
        try:
            data = json.loads(json_slice)
        except:
            logger.error(f"error parsing json={json_slice}")
            raise

    logger.debug(f"parsed message={data}")
    return {output_key: data}


class ParseJSON(Chain):
    """
    Chain that parses AI response content into JSON
    """

    # input/output key map
    input_key: str = "text"
    output_key: str = "json"

    @property
    def output_keys(self) -> List[str]:
        # TODO: does this need to list all known outputs?
        return [self.output_key]

    @property
    def input_keys(self) -> List[str]:
        """Input keys this chain expects."""
        return [self.input_key]

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        return parse_json(inputs[self.input_key], self.output_key)

    async def _acall(self, inputs: Dict[str, str]) -> Dict[str, str]:
        return parse_json(inputs[self.input_key], self.output_key)

    @classmethod
    def from_config(cls, config: Dict[str, Any], callback_manager: IxCallbackManager):
        return cls(**config, callback_manager=callback_manager)
