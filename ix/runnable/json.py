import dataclasses
from enum import Enum
from typing import Dict, Any, Optional, Union, List
from jsonpath_ng import parse as jsonpath_parse

from langchain.schema.runnable import RunnableSerializable, RunnableConfig
from langchain.schema.runnable.utils import Input, Output

from ix.utils.json import to_json_serializable


class BaseType(Enum):
    """"""

    SINGLE = 1
    LIST = 2
    OBJECT = 3


@dataclasses.dataclass
class JSONPath:
    """JSON Path with an option to return results as a list."""

    path: str
    is_list: bool = False


JSONTransform = Union[JSONPath, List[JSONPath], Dict[str, JSONPath]]


class RunJSONTransform(RunnableSerializable[Input, Output]):
    """
    Transform a JSON object using JSONPath(s). May return a single value,
    a list of values, or a dictionary of values. Lists are dictionaries are
    built from matching structures containing JSONPath

    Base object modes:
    - Single: return a single using a JSONPath.
    - List: return a list of values for a list of JSONPaths
    - Object: return a dictionary of values from a dict of JSONPath.
    """

    base: BaseType
    """Type of object to be returned by the transform"""

    json_path: JSONTransform
    """JSON Path(s) for transformation."""

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Is this class serializable?"""
        return True

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Output:
        formatted_input = to_json_serializable(input, truncate=False)
        return self._process_json_path(formatted_input)

    async def ainvoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Output:
        formatted_input = to_json_serializable(input, truncate=False)
        return self._process_json_path(formatted_input)

    def _process_json_path(self, input_data: Dict[str, Any]) -> Output:
        if self.base == BaseType.SINGLE:
            return self._extract_single(input_data)
        elif self.base == BaseType.LIST:
            return self._extract_list(input_data)
        elif self.base == BaseType.OBJECT:
            return self._extract_object(input_data)
        else:
            raise ValueError(f"Invalid transform_type mode: {self.base}")

    def _extract_single(self, input_data: Dict[str, Any]) -> Any:
        jsonpath_expr = jsonpath_parse(self.json_path.path)
        matches = jsonpath_expr.find(input_data)
        if not matches and self.json_path.is_list:
            return []
        return (
            [match.value for match in matches]
            if self.json_path.is_list
            else (matches[0].value if matches else None)
        )

    def _extract_list(self, input_data: Dict[str, Any]) -> List[Any]:
        results = []
        for json_path in self.json_path:
            jsonpath_expr = jsonpath_parse(json_path.path)
            matches = jsonpath_expr.find(input_data)
            if json_path.is_list:
                # If is_list is True, append a list of all matches
                results.append([match.value for match in matches])
            else:
                # If is_list is False, append the first match value or None if no matches
                results.extend([match.value for match in matches])
        return results

    def _extract_object(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        for key, json_path in self.json_path.items():
            jsonpath_expr = jsonpath_parse(json_path.path)
            matches = jsonpath_expr.find(input_data)
            match_values = [match.value for match in matches]
            results[key] = (
                match_values
                if json_path.is_list
                else (match_values[0] if match_values else None)
            )
        return results
