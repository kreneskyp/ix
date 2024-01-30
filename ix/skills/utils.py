import ast
import json
import os
import subprocess
import textwrap
from typing import Dict, Any, Optional

from langchain_experimental.utilities import PythonREPL


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


def run_code_with_repl(
    code: str, function: str, input: Dict[str, Any], timeout: Optional[int] = None
) -> str:
    # HAX: use globals for I/O with the REPL. Hacky way to avoid serialization.
    func_output = []
    repl = PythonREPL(_globals={"func_input": input, "func_output": func_output})

    # Prepare the command to run in the REPL
    command = textwrap.dedent(
        f"""
{code}
output = {function}(**func_input)
func_output.append(output)
"""
    )

    print(input)
    print(command)

    # Run the command in the PythonREPL
    repl.run(command, timeout)

    print(func_output)

    return func_output[0]
