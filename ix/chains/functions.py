import json
import logging
from typing import Any, TypedDict, List, TypeVar, Tuple, Dict, Callable, Union

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.chains.openai_functions.openapi import openapi_spec_to_openai_fn
from langchain.schema import BaseLLMOutputParser, Generation
from langchain.utilities.openapi import OpenAPISpec

T = TypeVar("T")


logger = logging.getLogger(__name__)


class FunctionSchema(TypedDict):
    name: str
    description: str
    parameters: Any


class OpenAPIFunctionsToolkit(BaseToolkit):
    name = "OpenAPI Functions"
    description = "OpenAPI Functions"
    spec: Union[OpenAPISpec, str]

    def get_tools(self) -> Tuple[List[Dict[str, Any]], Callable]:
        for conversion in (
            OpenAPISpec.from_url,
            OpenAPISpec.from_file,
            OpenAPISpec.from_text,
        ):
            try:
                spec = conversion(self.spec)
                break
            except Exception:
                pass
            if isinstance(spec, str):
                raise ValueError(f"Unable to parse spec from source {spec}")
        openai_fns, call_api_fn = openapi_spec_to_openai_fn(spec)

        # TODO: Need to convert into a list of tools

        return tools


class OpenAIFunctionParser(BaseLLMOutputParser):
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
