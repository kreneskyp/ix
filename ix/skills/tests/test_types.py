import pytest

from ix.skills.tests.test_utils import (
    expected_schemas,
    FUNC_WITH_VARS_SCRIPT,
    FUNC_WITH_COMPOUND_TYPE_SCRIPT,
    FUNC_WITH_DOCSTRING_SCRIPT,
    SCRIPT_WITH_MULTIPLE_FUNCS_SCRIPT,
    SCRIPT_WITH_MULTIPLE_FUNCS_NO_RUN_SCRIPT,
    FUNC_WITHOUT_TYPE_HINTS_SCRIPT,
)
from ix.skills.types import EditSkill


class TestNewSkill:
    def test_new_skill_initialization_with_vars(self):
        skill = EditSkill(name="Test Skill", code=FUNC_WITH_VARS_SCRIPT, tags=[])
        assert skill.func_name == "test_func"
        assert skill.input_schema == expected_schemas["func_with_vars"]

        # function does not have a docstring
        assert skill.description == "this is a test."

    def test_new_skill_initialization_with_compound_type(self):
        skill = EditSkill(
            name="Test Skill", code=FUNC_WITH_COMPOUND_TYPE_SCRIPT, tags=[]
        )
        assert skill.func_name == "test_func"
        assert skill.input_schema == expected_schemas["func_with_compound_type"]

    def test_new_skill_initialization_with_docstring(self):
        skill = EditSkill(name="Test Skill", code=FUNC_WITH_DOCSTRING_SCRIPT, tags=[])
        assert skill.func_name == "test_func"
        expected_description = "This is a test function."
        assert skill.description == expected_description

    def test_new_skill_initialization_with_multiple_funcs(self):
        skill = EditSkill(
            name="Test Skill", code=SCRIPT_WITH_MULTIPLE_FUNCS_SCRIPT, tags=[]
        )
        assert skill.func_name == "run"

    def test_new_skill_initialization_with_multiple_funcs_no_run(self):
        with pytest.raises(ValueError):
            EditSkill(
                name="Test Skill",
                code=SCRIPT_WITH_MULTIPLE_FUNCS_NO_RUN_SCRIPT,
                tags=[],
            )

    def test_new_skill_initialization_with_func_name_override(self):
        overridden_func_name = "func1"
        skill = EditSkill(
            name="Test Skill",
            code=SCRIPT_WITH_MULTIPLE_FUNCS_SCRIPT,
            tags=[],
            func_name=overridden_func_name,
        )
        assert skill.func_name == overridden_func_name

    def test_new_skill_initialization_without_type_hints(self):
        with pytest.raises(ValueError):
            EditSkill(name="Test Skill", code=FUNC_WITHOUT_TYPE_HINTS_SCRIPT, tags=[])
