import json
import logging
from typing import Any, List, TypeVar, Dict
from langchain.schema import BaseLLMOutputParser, Generation
from pydantic import BaseModel, model_validator

T = TypeVar("T")


logger = logging.getLogger(__name__)


class FunctionSchema(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

    @model_validator(mode="before")
    def validate_parameters(cls, values):
        if isinstance(values["parameters"], str):
            values["parameters"] = json.loads(values["parameters"])
        return values


class OpenAIFunctionParser(BaseLLMOutputParser, BaseModel):
    """
    OpenAI function parser. This parser is used to parse a function call
    out of a response. This is used in conjunction with functions attached
    to the LLMChain.

    The function_call is returned if present, otherwise the text is returned.

    if parse_json is True, the function_call is parsed as JSON. Otherwise,
    it is returned as provided by the LLM component. This may be a string,
    dict, or combination of both (arguments may be a string).
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
