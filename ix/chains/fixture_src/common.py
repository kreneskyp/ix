VERBOSE = {
    "name": "verbose",
    "type": "boolean",
    "default": False,
}

TAGS = {
    "name": "tags",
    "type": "list",
    "default": [],
    "style": {
        "width": "100%",
    },
}

METADATA = {
    "name": "metadata",
    "type": "dict",
    "required": False,
}

INPUT_VARIABLES = {
    "name": "input_variables",
    "type": "list",
    "default": [],
    "style": {
        "width": "100%",
    },
}

CHAIN_BASE_FIELDS = [VERBOSE, TAGS]
