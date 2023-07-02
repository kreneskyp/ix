from ix.chains.fixture_src.tools import TOOL_BASE_FIELDS


TOOL_BASE_FIELD_NAMES = {tool["name"] for tool in TOOL_BASE_FIELDS}


def extract_tool_kwargs(kwargs: dict) -> dict:
    """
    Extract tool kwargs from kwargs.
    """
    tool_kwargs = {}
    for key, value in list(kwargs.items()):
        if key in TOOL_BASE_FIELD_NAMES:
            tool_kwargs[key] = kwargs.pop(key)
    return tool_kwargs
