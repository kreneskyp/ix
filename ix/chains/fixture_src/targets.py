RUNNABLE_TYPES = [
    "agent",
    "chain",
    "document_loader",
    "llm",
    "prompt",
    "retriever",
    "text_splitter",
    "tool",
]
FLOW_CONTROL_TYPES = ["root", "branch", "map", "flow"]
FLOW_TYPES = sorted(RUNNABLE_TYPES + FLOW_CONTROL_TYPES)


EMBEDDINGS_TARGET = {
    "key": "embedding",
    "type": "target",
    "source_type": "embeddings",
}

LLM_TARGET = {
    "key": "llm",
    "type": "target",
    "source_type": "llm",
    "required": True,
}

MEMORY_BACKEND_TARGET = {
    "key": "chat_memory",
    "type": "target",
    "source_type": "memory_backend",
    "required": True,
}

OUTPUT_PARSER_TARGET = {
    "key": "output_parser",
    "type": "target",
    "source_type": "output_parser",
}

PROMPT_TARGET = {
    "key": "prompt",
    "type": "target",
    "source_type": "prompt",
}

MEMORY_TARGET = {
    "key": "memory",
    "type": "target",
    "source_type": "memory",
    "multiple": True,
}

SEQUENCE_CHAINS_TARGET = {
    "key": "chains",
    "type": "target",
    "source_type": "chain",
    "auto_sequence": False,
}

CHAIN_TARGET = {
    "key": "chain",
    "type": "target",
    "source_type": "chain",
}

WORKFLOW_SOURCE = {
    "key": "workflow",
    "type": "source",
    "source_type": FLOW_TYPES,
    "collection": "flow",
}

FUNCTION_TARGET = {
    "key": "functions",
    "type": "target",
    "source_type": ["tool", "toolkit", "schema"],
    "multiple": True,
    "auto_sequence": False,
}

VECTORSTORE_TARGET = {
    "key": "vectorstore",
    "type": "target",
    "source_type": "vectorstore",
    "required": True,
}

TOOLS_TARGET = {
    "key": "tools",
    "type": "target",
    "source_type": ["tool", "toolkit"],
    "multiple": True,
    "as_type": "tool",
}

PARSER_TARGET = {
    "key": "parser",
    "type": "target",
    "source_type": "parser",
}

DOCUMENT_LOADER_TARGET = {
    "key": "document_loader",
    "type": "target",
    "source_type": "document_loader",
    "required": True,
}

DOCUMENTS_TARGET = {
    "key": "documents",
    "type": "target",
    "source_type": "text_splitter",
}

RETRIEVER_TARGET = {
    "key": "retriever",
    "type": "target",
    "source_type": ["retriever", "vectorstore"],
    "as_type": "retriever",
    "required": True,
}
