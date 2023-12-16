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
    "description": "Template for Chat style LLM request. Renders System, User, and AI messages",
    "connectors": [
        {
            "key": "out",
            "label": "Prompt",
            "type": "source",
            "source_type": "prompt",
        },
        # HAX: disabled for now because this might not work.
        # {
        #    "key": "in",
        #    "label": "Input",
        #    "type": "target",
        #    "from_field": "input_variables",
        #    "source_type": FLOW_TYPES,
        # },
    ],
    "fields": [
        {
            "name": "messages",
            "type": "list",
            "default": DEFAULT_MESSAGES,
        }
    ],
}
