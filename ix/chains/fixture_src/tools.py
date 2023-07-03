from ix.chains.fixture_src.common import VERBOSE

DESCRIPTION = {
    "name": "description",
    "type": "str",
    "default": "",
}

RETURN_DIRECT = {
    "name": "return_direct",
    "type": "boolean",
    "default": False,
}

TOOL_BASE_FIELDS = [DESCRIPTION, RETURN_DIRECT, VERBOSE]

GOOGLE_SEARCH = {
    "class_path": "ix.tools.google.get_google_search",
    "type": "tool",
    "name": "Google Search",
    "description": "Tool that searches Google for a given query.",
    "fields": TOOL_BASE_FIELDS + [],
}

GOOGLE_SERPER = {
    "class_path": "ix.tools.google.get_google_search",
    "type": "tool",
    "name": "Google Search",
    "description": "Tool that searches Google for a given query.",
    "fields": TOOL_BASE_FIELDS + [],
}


WOLFRAM = {
    "name": "Wolfram Alpha",
    "description": "Wolfram Alpha search engine for math and science",
    "class_path": "ix.tools.wolfram_alpha.get_wolfram_alpha",
    "display_type": "node",
    "type": "tool",
    "fields": TOOL_BASE_FIELDS
    + [
        {
            "name": "wolfram_alpha_app_id",
            "label": "Wolfram Alpha App ID",
            "type": "str",
            "input": "secret",
        },
    ],
}


TOOLS = [
    GOOGLE_SEARCH,
    WOLFRAM,
]
