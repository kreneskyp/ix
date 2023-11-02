CHAIN_REFERENCE_CLASS_PATH = "ix.chains.routing.ChainReference.load_from_id"
CHAIN_REFERENCE = {
    "class_path": CHAIN_REFERENCE_CLASS_PATH,
    "type": "chain",
    "name": "Chain Reference",
    "description": "Embed a chain in another chain. The chain is called as if it were a component in the local flow.",
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


REFERENCES = [CHAIN_REFERENCE]
