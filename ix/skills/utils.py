import ast
import json
import os
import subprocess
import sys
import textwrap
import traceback
from typing import Dict, Any, Optional

from langchain_experimental.utilities import PythonREPL
from pydantic import BaseModel


class MissingTypeHintError(Exception):
    """Exception raised when type hints are missing for function parameters."""

    pass


class AmbiguousFuncName(Exception):
    """Exception raised when multiple functions are found in the code and none are "run"."""

    pass


def demote(user_uid, user_gid):
    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)

    return result


def extract_func(code: str, func_name: str) -> str:
    dedented_code = textwrap.dedent(code)

    # Construct the wrapper code without nested f-strings
    wrapper_code = f"""
import json
import pydantic
from ix.utils.pydantic import model_from_signature

{dedented_code}

try:
    model = model_from_signature("FuncArgs", {func_name})
    print(json.dumps({{"schema": model.schema()}}))
except pydantic.errors.PydanticInvalidForJsonSchema as e:
    print(json.dumps({{"error": "MissingTypeHintError"}}))
"""

    process = subprocess.Popen(
        ["python3", "-c", wrapper_code],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise ValueError(f"Error in executing the script: {stderr}")

    result_json = json.loads(stdout)
    if "error" in result_json and result_json["error"] == "MissingTypeHintError":
        raise MissingTypeHintError("Type hints are missing for some parameters.")

    return result_json.get("schema")


def parse_skill(
    code: str,
    provided_func_name: Optional[str] = None,
    input_schema: Optional[dict] = None,
) -> tuple[str, dict, Optional[str]]:
    func_name = provided_func_name
    tree = ast.parse(code)
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    if not func_name:
        if len(functions) > 1 and not any(func.name == "run" for func in functions):
            raise AmbiguousFuncName(
                "Multiple functions found and none are named 'run'."
            )
        func_name = (
            "run"
            if any(func.name == "run" for func in functions)
            else functions[0].name
            if functions
            else None
        )

    if not func_name:
        raise ValueError("Function name could not be determined from code")

    description = None
    for func in functions:
        if func.name == func_name:
            description = ast.get_docstring(func)
            break

    if not input_schema:
        input_schema = extract_func(code, func_name)

    return func_name, input_schema, description


class ErrorResponse(BaseModel):
    message: str
    traceback: str
    line: int


def execute_function(function, raise_errors: bool = False):
    try:
        result = function()
        return result
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        error_response = ErrorResponse(
            message=str(e),
            traceback="".join(traceback.format_tb(exc_tb)),
            line=line_number,
        )
        if raise_errors:
            raise e
        else:
            return error_response


def run_code_with_repl(
    code: str,
    function: str,
    input: Dict[str, Any],
    timeout: Optional[int] = None,
    raise_errors: bool = False,
) -> Any:
    # HAX: use globals for I/O with the REPL. Hacky way to avoid serialization.
    func_output = []
    repl = PythonREPL(
        _globals={
            "func_input": input,
            "func_output": func_output,
            "json": json,
            "ErrorResponse": ErrorResponse,
        }
    )

    # Prepare the command to run in the REPL
    command = textwrap.dedent(
        f"""
import traceback
import sys

{code}

try:
    output = {function}(**func_input)
    func_output.append(output)
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    error_response = ErrorResponse(
        message=str(e),
        traceback=''.join(traceback.format_tb(exc_tb)),
        line=exc_tb.tb_lineno
    )
    func_output.append(error_response)
    if raise_errors:
        raise e
"""
    )

    # Run the command in the PythonREPL
    response = repl.run(command, timeout)
    output = func_output[0] if func_output else response

    if isinstance(output, ErrorResponse) and raise_errors:
        raise Exception(output.message)

    return output
