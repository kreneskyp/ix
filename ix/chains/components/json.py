from typing import Dict, Any, Optional
from jsonpath_ng import parse as jsonpath_parse

from langchain.schema.runnable import RunnableSerializable, RunnableConfig
from langchain.schema.runnable.utils import Input, Output


class JSONPath(RunnableSerializable[Input, Output]):
    """Parse a value from inputs using a JSONPath"""

    path: str
    """JSON Path to load."""

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ):
        jsonpath_expr = jsonpath_parse(self.path)
        json_matches = jsonpath_expr.find(input)
        if len(json_matches) == 0:
            raise ValueError(f"could not find input at {self.path} searched: {input}")

        value = json_matches[0].value
        return value
