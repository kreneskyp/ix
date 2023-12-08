from ix.chains.fixture_src.targets import FLOW_TYPES

ROOT_CLASS_PATH = "__ROOT__"
ROOT_NODE = {
    "class_path": ROOT_CLASS_PATH,
    "name": "Chat Input",
    "description": "Input from a chat window.",
    "type": "root",
    "connectors": [
        # {
        #    "type": "source",
        #    "from_config": "inputs",
        # }
    ],
    "fields": [
        {
            "name": "outputs",
            "label": "Inputs",
            "type": "list",
            "input_type": "hash_list",
            "description": "Inputs from the chat API.",
            "default": [
                "user_input",
                "artifact_ids",
            ],
        },
        {
            "name": "outputs_hash",
            "type": "list",
            "input_type": "hidden",
            "description": "Input from a chat window.",
            "default": [
                "user_input",
                "artifact_ids",
            ],
        },
    ],
}

MERGE_LIST_CLASS_PATH = "ix.runnable.flow.MergeList"
MERGE_LIST = {
    "class_path": MERGE_LIST_CLASS_PATH,
    "name": "Merge List",
    "description": "Combine multiple inputs into a list.",
    "type": "node",
    "connectors": [
        {
            "key": "in",
            "label": "Inputs",
            "type": "source",
            "from_field": "outputs",
            "source_type": FLOW_TYPES,
        },
    ],
}

FLOW = [ROOT_NODE, MERGE_LIST]
