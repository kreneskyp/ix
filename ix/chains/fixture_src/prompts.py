from ix.chains.fixture_src.targets import OUTPUT_PARSER_TARGET

DEFAULT_MESSAGES = [
    {
        "role": "system",
        "template": "",
        "input_variables": [],
    }
]

CHAT_PROMPT_TEMPLATE = {
    "class_path": "langchain.prompts.chat.ChatPromptTemplate",
    "type": "prompt",
    "name": "Chat Prompt Template",
    "description": "Template for constructing chat prompts from messages.",
    "connectors": [OUTPUT_PARSER_TARGET],
    "fields": [
        {
            "name": "messages",
            "type": "list",
            "default": DEFAULT_MESSAGES,
        }
    ],
}
