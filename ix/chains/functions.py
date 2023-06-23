import json
import logging
from typing import Any, TypedDict, List
from langchain.schema import BaseLLMOutputParser, Generation, T


logger = logging.getLogger(__name__)


class FunctionSchema(TypedDict):
    name: str
    description: str
    parameters: Any


class OpenAIFunctionParser(BaseLLMOutputParser):
    """
    OpenAI function parser. This parser is used to parse the a function call
    out of the response. This is used in conjunction with functions attached
    to the LLMChain.

    The function_call is returned if present, otherwise the text is returned.
    """

    parse_json: bool = False

    def parse_result(self, result: List[Generation]) -> T:
        additional_kwargs = result[0].message.additional_kwargs
        if "function_call" in additional_kwargs:
            function_call = additional_kwargs["function_call"]
            if self.parse_json:
                if isinstance(function_call, str):
                    function_call = json.loads(function_call)

                if isinstance(function_call["arguments"], str):
                    function_call["arguments"] = json.loads(function_call["arguments"])

            return function_call
        else:
            return result[0].text
