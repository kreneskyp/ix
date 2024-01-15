import json
from pathlib import Path


from ix.chains.fixture_src.chains import CONVERSATIONAL_RETRIEVAL_CHAIN_CLASS_PATH
from ix.chains.fixture_src.document_loaders import GENERIC_LOADER_CLASS_PATH
from ix.chains.fixture_src.embeddings import OPENAI_EMBEDDINGS_CLASS_PATH
from ix.chains.fixture_src.lcel import RUNNABLE_EACH_CLASS_PATH
from ix.chains.fixture_src.parsers import LANGUAGE_PARSER_CLASS_PATH
from ix.chains.fixture_src.text_splitter import RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH
from ix.chains.fixture_src.vectorstores import (
    REDIS_VECTORSTORE_CLASS_PATH,
)

from ix.chains.fixture_src.tools import GOOGLE_SEARCH

OPENAI_LLM = {
    "class_path": "langchain_community.chat_models.ChatOpenAI",
    "config": {"verbose": True},
}

OPENAI_FUNCTION_SCHEMA = {
    "class_path": "ix.runnable.schema.Schema",
    "name": "openai_function",
    "description": "Run an OpenAI function.",
    "config": {
        "parameters": json.dumps(
            {
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "filename": {"type": "string"},
                                "description": {"type": "string"},
                            },
                            "required": ["filename", "description"],
                        },
                    },
                },
            },
            indent=4,
        ),
    },
}

MOCK_MEMORY = {
    "class_path": "ix.chains.tests.mock_memory.MockMemory",
    "config": {"value_map": {"mock_memory_input": "mock memory"}},
}

MEMORY = {
    "class_path": "langchain.memory.ConversationBufferMemory",
    "config": {
        "input_key": "user_input",
        "memory_key": "chat_history",
    },
}

MEMORY_WITH_BACKEND = {
    "class_path": "langchain.memory.ConversationBufferMemory",
    "config": {
        "input_key": "user_input",
        "memory_key": "chat_history",
        "chat_memory": {
            "class_path": "langchain.memory.RedisChatMessageHistory",
            "config": {"url": "redis://redis:6379/0", "session_scope": "task"},
        },
    },
}

MEMORY_WITH_LLM = {
    "class_path": "langchain.memory.summary_buffer.ConversationSummaryBufferMemory",
    "config": {
        "input_key": "user_input",
        "memory_key": "chat_summary",
        "llm": {
            "class_path": "langchain_community.chat_models.ChatOpenAI",
        },
    },
}

AGENT_MEMORY = {
    "class_path": "langchain.memory.ConversationBufferMemory",
    "config": {
        "input_key": "user_input",
        "memory_key": "chat_history",
        # agent requires return_messages=True
        "return_messages": True,
    },
}

MEMORY_WITH_SCOPE = {
    "class_path": "ix.memory.artifacts.ArtifactMemory",
    "config": {
        "memory_key": "chat_history",
        "session_scope": "chat",
        "session_prefix": "tests",
    },
}

CHAT_MESSAGES = [
    {
        "role": "system",
        "template": "You are a test bot.",
    },
    {
        "role": "user",
        "template": "{user_input}",
        "input_variables": ["user_input"],
    },
]

CHAT_MESSAGES_WITH_CHAT_HISTORY = [
    {
        "role": "system",
        "template": "You are a test bot! HISTORY: {chat_history}",
        "input_variables": ["chat_history"],
    },
    {
        "role": "user",
        "template": "{user_input}",
        "input_variables": ["user_input"],
    },
]

PROMPT_CHAT = {
    "class_path": "langchain.prompts.chat.ChatPromptTemplate",
    "config": {
        "messages": CHAT_MESSAGES,
    },
}

PROMPT_CHAT_0 = {
    "class_path": "langchain.prompts.chat.ChatPromptTemplate",
    "config": {
        "messages": [
            {
                "role": "system",
                "template": "You are bot 0.",
            }
        ],
    },
}

PROMPT_CHAT_1 = {
    "class_path": "langchain.prompts.chat.ChatPromptTemplate",
    "config": {
        "messages": [
            {
                "role": "system",
                "template": "You are bot 1.",
            }
        ],
    },
}

PROMPT_CHAT_2 = {
    "class_path": "langchain.prompts.chat.ChatPromptTemplate",
    "config": {
        "messages": [
            {
                "role": "system",
                "template": "You are bot 2.",
            }
        ],
    },
}

PROMPT_WITH_CHAT_HISTORY = {
    "class_path": "langchain.prompts.chat.ChatPromptTemplate",
    "config": {
        "messages": CHAT_MESSAGES_WITH_CHAT_HISTORY,
    },
}

LLM_CHAIN = {
    "class_path": "ix.chains.llm_chain.LLMChain",
    "config": {
        "prompt": PROMPT_CHAT,
        "llm": {
            "class_path": "langchain_community.chat_models.ChatOpenAI",
        },
    },
}

LLM_REPLY = {
    "class_path": "ix.chains.llm_chain.LLMReply",
    "config": {
        "prompt": PROMPT_CHAT,
        "llm": {
            "class_path": "langchain_community.chat_models.ChatOpenAI",
        },
    },
}

LLM_REPLY_WITH_HISTORY = {
    "class_path": "ix.chains.llm_chain.LLMReply",
    "config": {
        "prompt": PROMPT_WITH_CHAT_HISTORY,
        "llm": {
            "class_path": "langchain_community.chat_models.ChatOpenAI",
        },
    },
}

LLM_REPLY_WITH_HISTORY_AND_MEMORY = {
    "class_path": "ix.chains.llm_chain.LLMReply",
    "config": {
        "prompt": PROMPT_WITH_CHAT_HISTORY,
        "memory": MEMORY,
        "llm": {
            "class_path": "langchain_community.chat_models.ChatOpenAI",
        },
    },
}

GOOGLE_SEARCH_CONFIG = {
    "class_path": GOOGLE_SEARCH["class_path"],
    "name": "tester",
    "description": "test",
    "config": {},
}

TEST_DATA = Path("/var/app/test_data")
TEST_DOCUMENTS = TEST_DATA / "documents"

LANGUAGE_PARSER = {
    "class_path": LANGUAGE_PARSER_CLASS_PATH,
    "config": {
        "language": "python",
    },
}

DOCUMENT_LOADER = {
    "class_path": GENERIC_LOADER_CLASS_PATH,
    "config": {
        "parser": LANGUAGE_PARSER,
        "path": str(TEST_DOCUMENTS),
        "suffixes": [".py"],
    },
}

TEXT_SPLITTER = {
    "class_path": RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH,
    "config": {"language": "python", "document_loader": DOCUMENT_LOADER},
}

EMBEDDINGS = {
    "class_path": OPENAI_EMBEDDINGS_CLASS_PATH,
    "config": {"model": "text-embedding-ada-002"},
}

REDIS_VECTORSTORE = {
    "class_path": REDIS_VECTORSTORE_CLASS_PATH,
    "config": {
        "embedding": EMBEDDINGS,
        "redis_url": "redis://redis:6379/0",
        "index_name": "tests",
    },
}

CONVERSATIONAL_RETRIEVAL_CHAIN = {
    "class_path": CONVERSATIONAL_RETRIEVAL_CHAIN_CLASS_PATH,
    "config": {"llm": OPENAI_LLM, "retriever": REDIS_VECTORSTORE},
}

RUNNABLE_EACH = {"class_path": RUNNABLE_EACH_CLASS_PATH, "config": {}}
