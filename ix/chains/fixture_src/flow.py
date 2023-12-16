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

CHAIN_REF_CLASS_PATH = "ix.runnable.flow.load_chain_id"
CHAIN_REF = {
    "class_path": CHAIN_REF_CLASS_PATH,
    "name": "Chain Reference",
    "description": "Embed a chain in another chain. The chain is called as if it were a component in the local flow.",
    "type": "chain",
    "context": "context",
    "fields": [
        {
            "name": "chain_id",
            "label": "Chain",
            "type": "string",
            "input_type": "IX:chain",
            "required": True,
            "description": "The chain to embed.",
        }
    ],
}

FLOW = [ROOT_NODE, CHAIN_REF]
