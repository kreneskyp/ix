import pytest

from ix.utils.config import format_config, get_config_variables, TemplateException


@pytest.fixture
def sample_config():
    return {
        "name": "{username}",
        "details": {"age": "{age}", "address": "{address}"},
        "hobbies": ["{hobby1}", "{hobby2}"],
        "escape_test1": "{{escaped_double_braces}}",
        "escape_test2": "{{escaped_single_braces}",
    }


@pytest.fixture
def sample_variables():
    return {
        "username": "John",
        "age": "25",
        "address": "1234 Elm St",
        "hobby1": "reading",
        "hobby2": "writing",
    }


class TestFormatConfig:
    def test_format(self, sample_config, sample_variables):
        formatted_config = format_config(sample_config, sample_variables)
        assert formatted_config["name"] == "John"
        assert formatted_config["details"]["age"] == "25"
        assert formatted_config["details"]["address"] == "1234 Elm St"
        assert formatted_config["hobbies"] == ["reading", "writing"]
        assert formatted_config["escape_test1"] == "{escaped_double_braces}"
        assert formatted_config["escape_test2"] == "{escaped_single_braces}"

    def test_format_with_missing_variables(self, sample_config):
        variables = {"username": "John"}
        with pytest.raises(TemplateException, match="Missing variable: age"):
            format_config(sample_config, variables)

    def test_format_with_non_string_values(self):
        config = {
            "integer": 123,
            "float": 123.45,
            "boolean": True,
        }
        formatted_config = format_config(config, {})
        assert formatted_config == config


class TestGetConfigVariables:
    def test_get_variables(self, sample_config):
        variables = get_config_variables(sample_config)
        assert variables == {"username", "age", "address", "hobby1", "hobby2"}

    def test_get_variables_with_no_variables(self):
        config = {
            "escape_test1": "{{escaped_double_braces}}",
            "escape_test2": "{{escaped_single_braces}",
        }
        variables = get_config_variables(config)
        assert not variables
