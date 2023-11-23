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

FLOW = [ROOT_NODE]
