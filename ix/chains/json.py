import json
import logging
from typing import Dict, Any, List

from langchain.chains.base import Chain

from ix.agents.callback_manager import IxCallbackManager
from ix.agents.exceptions import MissingCommandMarkers


logger = logging.getLogger(__name__)


class ParseJSON(Chain):
    """Chain that parses AI response content into JSON"""

    @property
    def output_keys(self) -> List[str]:
        # TODO: does this need to list all known outputs?
        return ["ai_json"]

    @property
    def input_keys(self) -> List[str]:
        """Input keys this chain expects."""
        return ["text"]

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        return self.parse_response(inputs["text"])

    async def _acall(self, inputs: Dict[str, str]) -> Dict[str, str]:
        return self.parse_response(inputs["text"])

    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse response into valid JSON"""
        start_marker = "###START###"
        end_marker = "###END###"
        start_index = response.find(start_marker)
        end_index = response.find(end_marker)

        if start_index == -1 or end_index == -1:
            # before raising attempt to parse the response as json
            # sometimes the AI returns responses that are still usable even without the markers
            try:
                data = json.loads(response.strip())
            except Exception:
                raise MissingCommandMarkers
        else:
            json_slice = response[start_index + len(start_marker) : end_index].strip()
            data = json.loads(json_slice)

        logger.debug(f"parsed message={data}")
        return {"ai_json": data}

    @classmethod
    def from_config(cls, config: Dict[str, Any], callback_manager: IxCallbackManager):
        return cls(**config, callback_manager=callback_manager)
