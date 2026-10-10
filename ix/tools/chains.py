from ix.chains.fixture_src.targets import LLM_TARGET


LLM_MATH = {
    "name": "LLM Math",
    "description": "LLM Math",
    "key": "llm_math",
    "class_path": "langchain.agents.load_tools._get_llm_math",
    "type": "tool",
    "config": {
        "connectors": [LLM_TARGET],
    },
    "fields": [],
}
