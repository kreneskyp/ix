import re
from typing import Any, Dict, Set


class TemplateException(Exception):
    pass


# matches {variables} but not {{escaped_variables}}
VARIABLE_REGEX = r"(?<!\{)\{(\w+)\}"

# matches {{escaped_variables}}
ESCAPED_VARIABLE_REGEX = r"\{\{(\w+)\}?\}"


def format_config(config: Any, variables: Dict[str, Any]) -> Any:
    """
    Recursively update the `config` object by replacing $variables.

    Escaped variables $$variable will be replaced with $variable.

    Parameters:
    config (Any): The configuration object. It can be a nested structure containing dictionaries and lists.
    variables (Dict[str, Any]): The dictionary containing the variable names and their corresponding values.

    Returns:
    Any: The updated configuration object.
    """
    if isinstance(config, dict):
        return {k: format_config(v, variables) for k, v in config.items()}
    elif isinstance(config, list):
        return [format_config(elem, variables) for elem in config]
    elif isinstance(config, str):
        # Handle regular variables
        def regular_replacer(match):
            var_name = match.group(1)
            if var_name not in variables:
                raise TemplateException(f"Missing variable: {var_name}")
            return str(variables.get(var_name))

        config = re.sub(VARIABLE_REGEX, regular_replacer, config)

        # Handle escaped variables second
        def escaped_replacer(match):
            return "{" + match.group(1) + "}"

        config = re.sub(ESCAPED_VARIABLE_REGEX, escaped_replacer, config)

        return config
    else:
        return config


def get_config_variables(config: Dict[str, Any]) -> Set[str]:
    """
    Get all variables from a config dict.
    Will search recursively through nested dicts and lists.
    """
    variables = set()
    if isinstance(config, dict):
        for key, value in config.items():
            variables.update(get_config_variables(value))
    elif isinstance(config, list):
        for item in config:
            variables.update(get_config_variables(item))
    elif isinstance(config, str):
        matches = re.findall(VARIABLE_REGEX, config)
        for match in matches:
            variables.add(match)
    return variables
