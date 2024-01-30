import pytest

from ix.skills.utils import parse_skill, MissingTypeHintError, AmbiguousFuncName

FUNC_WITH_VARS_SCRIPT = '''
def test_func(a: int, b: int) -> None:
    """this is a test."""
    pass
'''

FUNC_WITH_COMPOUND_TYPE_SCRIPT = '''
from typing import List

def test_func(arg: List[str]) -> None:
    """this is a test."""
    pass
'''

FUNC_RETURNS_VALUE_SCRIPT = '''
def test_func() -> int:
    """this is a test."""
    return 42
'''

FUNC_WITH_DOCSTRING_SCRIPT = '''
def test_func():
    """This is a test function."""
    pass
'''


SCRIPT_WITH_MULTIPLE_FUNCS_SCRIPT = '''
def func1():
    """this is a test."""
    pass

def run():
    """this is a test."""
    pass
'''

SCRIPT_WITH_MULTIPLE_FUNCS_NO_RUN_SCRIPT = '''
def func1():
    """this is a test."""
    pass

def func2():
    """this is a test."""
    pass
'''

FUNC_WITHOUT_TYPE_HINTS_SCRIPT = '''
def test_func(a, b):
    """this is a test."""
    pass
'''


expected_schemas = {
    "func_with_vars": {
        "title": "FuncArgs",
        "type": "object",
        "properties": {
            "a": {"title": "A", "type": "integer"},
            "b": {"title": "B", "type": "integer"},
        },
        "required": ["a", "b"],
    },
    "func_with_compound_type": {
        "title": "FuncArgs",
        "type": "object",
        "properties": {
            "arg": {"title": "Arg", "type": "array", "items": {"type": "string"}}
        },
        "required": ["arg"],
    },
}


class TestSkillUtilityFunctions:
    def test_func_with_vars(self):
        func_name, input_schema, _ = parse_skill(FUNC_WITH_VARS_SCRIPT)
        assert func_name == "test_func"
        assert input_schema == expected_schemas["func_with_vars"]

    def test_func_with_compound_type(self):
        func_name, input_schema, _ = parse_skill(FUNC_WITH_COMPOUND_TYPE_SCRIPT)
        assert func_name == "test_func"
        assert input_schema == expected_schemas["func_with_compound_type"]

    def test_func_returns_value(self):
        func_name, _, _ = parse_skill(FUNC_RETURNS_VALUE_SCRIPT)
        assert func_name == "test_func"

    def test_func_with_docstring(self):
        func_name, _, description = parse_skill(FUNC_WITH_DOCSTRING_SCRIPT)
        assert func_name == "test_func"
        expected_description = "This is a test function."
        assert description == expected_description

    def test_script_with_multiple_funcs(self):
        func_name, _, _ = parse_skill(SCRIPT_WITH_MULTIPLE_FUNCS_SCRIPT)
        assert func_name == "run"

    def test_script_with_multiple_funcs_no_run(self):
        with pytest.raises(AmbiguousFuncName):
            parse_skill(SCRIPT_WITH_MULTIPLE_FUNCS_NO_RUN_SCRIPT)

    def test_func_name_override(self):
        overridden_func_name = "func1"
        func_name, _, _ = parse_skill(
            SCRIPT_WITH_MULTIPLE_FUNCS_SCRIPT, provided_func_name=overridden_func_name
        )
        assert func_name == overridden_func_name

    def test_func_without_type_hints(self):
        with pytest.raises(MissingTypeHintError):
            parse_skill(FUNC_WITHOUT_TYPE_HINTS_SCRIPT)
