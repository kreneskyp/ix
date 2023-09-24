import re
from typing import Any, Dict


def format_config(config: Any, variables: Dict[str, Any]) -> Any:
    """
    Recursively update the `config` object by replacing $variables.

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

        def replacer(match):
            whole, escaped, var = match.groups()
            if escaped:
                return whole
            return str(variables.get(var, whole))

        pattern = r"(\$\$)?\${([^}]*)}"
        return re.sub(pattern, replacer, config)
    else:
        return config
