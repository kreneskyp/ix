from copy import deepcopy

import pytest
from unittest.mock import MagicMock

from langchain.base_language import BaseLanguageModel
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryBufferMemory,
    CombinedMemory,
)
from langchain.schema import BaseChatMessageHistory, BaseMemory

from ix.agents.callback_manager import IxCallbackManager
from ix.chains.loaders.memory import get_memory_session
from ix.chains.tests.mock_memory import MockMemory
from ix.memory.artifacts import ArtifactMemory


class TestLoadLLM:
    pass


OPENAI_LLM = {
    "class_path": "langchain.chat_models.openai.ChatOpenAI",
    "config": {"verbose": True},
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
            "config": {"url": "redis://redis:6379/0", "session": {"scope": "task"}},
        },
    },
}

MEMORY_WITH_LLM = {
    "class_path": "langchain.memory.summary_buffer.ConversationSummaryBufferMemory",
    "config": {
        "input_key": "user_input",
        "memory_key": "chat_summary",
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
    },
}

MEMORY_WITH_SCOPE = {
    "class_path": "ix.memory.artifacts.ArtifactMemory",
    "config": {
        "memory_key": "chat_history",
        "session": {"scope": "chat", "prefix": "tests"},
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
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
    },
}

LLM_REPLY = {
    "class_path": "ix.chains.llm_chain.LLMReply",
    "config": {
        "prompt": PROMPT_CHAT,
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
    },
}

LLM_REPLY_WITH_HISTORY = {
    "class_path": "ix.chains.llm_chain.LLMReply",
    "config": {
        "prompt": PROMPT_WITH_CHAT_HISTORY,
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
    },
}

LLM_REPLY_WITH_HISTORY_AND_MEMORY = {
    "class_path": "ix.chains.llm_chain.LLMReply",
    "config": {
        "prompt": PROMPT_WITH_CHAT_HISTORY,
        "memory": MEMORY,
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
    },
}


@pytest.mark.django_db
class TestLoadMemory:
    def test_load_memory(self, load_chain):
        instance = load_chain(MEMORY)
        assert isinstance(instance, ConversationBufferMemory)

    def test_load_multiple(self, load_chain):
        """Test loading multiple memories into a CombinedMemory"""
        MEMORY2 = deepcopy(MEMORY)
        MEMORY2["config"]["memory_key"] = "chat_history2"

        LLM_CONFIG = deepcopy(LLM_REPLY_WITH_HISTORY)
        LLM_CONFIG["config"]["memory"] = [MEMORY, MEMORY2]
        chain = load_chain(LLM_CONFIG)
        instance = chain.memory
        assert isinstance(instance, CombinedMemory)
        assert len(instance.memories) == 2
        assert instance.memories[0].memory_key == "chat_history"
        assert instance.memories[1].memory_key == "chat_history2"

    def test_load_backend(self, load_chain):
        """
        A memory class can have a backend that separates memory logic from
        the storage system. ChatMemory works this way.
        """
        instance = load_chain(MEMORY_WITH_BACKEND)
        assert isinstance(instance, ConversationBufferMemory)
        assert isinstance(instance.chat_memory, BaseChatMessageHistory)

    def test_load_memory_with_scope(self, task, load_chain):
        """
        Test loading with a scope.

        Not all memories support sessions, for example ChatMemory
        adds scoping to the backend.
        """
        chat_id = task.leading_chats.first().id
        instance = load_chain(MEMORY_WITH_SCOPE)
        assert isinstance(instance, ArtifactMemory)
        assert instance.session_id == f"tests_chat_{chat_id}"

    def test_load_llm(self, load_chain, mock_openai):
        """
        Memory classes may optionally load an llm. (e.g. SummaryMemory)
        """
        instance = load_chain(MEMORY_WITH_LLM)
        assert isinstance(instance, ConversationSummaryBufferMemory)
        assert isinstance(instance.llm, BaseLanguageModel)

    def test_load_class_with_config(self, task, mocker, load_chain):
        """
        Test loading a class whose config is defined in MEMORY_CLASSES.
        This tests configuring an external class with the required config
        to integrate into Ix
        """
        chat_id = task.leading_chats.first().id

        # patch MEMORY_CLASSES to setup the test
        from ix.chains.loaders import memory

        mock_memory_classes = {
            MockMemory: {
                "supports_session": True,
            }
        }
        mocker.patch.object(memory, "MEMORY_CLASSES", mock_memory_classes)

        # load a memory that will use the mock class config
        instance = load_chain(
            {
                "class_path": "ix.chains.tests.mock_memory.MockMemory",
                "config": {
                    "session": {"scope": "chat", "prefix": "tests"},
                },
            },
        )
        assert isinstance(instance, MockMemory)
        assert instance.session_id == f"tests_chat_{chat_id}"


@pytest.mark.django_db
class TestLoadChatMemoryBackend:
    def test_load_chat_memory_backend(self, task, load_chain):
        chat_id = task.leading_chats.first().id

        # Config
        config = {
            "class_path": "langchain.memory.RedisChatMessageHistory",
            "config": {
                "url": "redis://redis:6379/0",
                "session": {"scope": "chat", "prefix": "tests"},
            },
        }

        # Run
        backend = load_chain(config)
        assert backend.session_id == f"tests_chat_{chat_id}"

    def test_load_defaults(self, task, load_chain):
        """
        ChatMemoryBackend should always load session_id. If `session` isn't present then
        load the `chat` scope by default.
        """

        chat_id = task.leading_chats.first().id

        # Config
        config = {
            "class_path": "langchain.memory.RedisChatMessageHistory",
            "config": {
                "url": "redis://redis:6379/0",
            },
        }

        # Run
        backend = load_chain(config)
        assert backend.session_id == f"chat_{chat_id}"


@pytest.mark.django_db
class TestGetMemorySession:
    """Test parsing the session scope from the chain config and runtime context."""

    @pytest.mark.parametrize(
        "config, cls, expected",
        [
            # No scope - defaults to chat
            (
                {"scope": "", "prefix": "123", "key": "session_id"},
                BaseChatMessageHistory,
                ("123_chat_1000", "session_id"),
            ),
            (
                {"scope": None, "prefix": "123", "key": "session_id"},
                BaseChatMessageHistory,
                ("123_chat_1000", "session_id"),
            ),
            (
                {"prefix": "123", "key": "session_id"},
                BaseChatMessageHistory,
                ("123_chat_1000", "session_id"),
            ),
            # agent, task, user scopes
            (
                {"scope": "agent", "prefix": "456", "key": "session_id"},
                BaseMemory,
                ("456_agent_1001", "session_id"),
            ),
            (
                {"scope": "task", "prefix": "789", "key": "session_id"},
                BaseMemory,
                ("789_task_1002", "session_id"),
            ),
            (
                {"scope": "user", "prefix": "321", "key": "session_id"},
                BaseChatMessageHistory,
                ("321_user_1003", "session_id"),
            ),
            # custom session_id_key
            (
                {"scope": "chat", "key": "chat_session"},
                BaseChatMessageHistory,
                ("chat_1000", "chat_session"),
            ),
            # no session prefix
            (
                {"scope": "chat", "key": "session_id"},
                BaseChatMessageHistory,
                ("chat_1000", "session_id"),
            ),
            # custom session prefix
            (
                {"scope": "chat", "prefix": "static_session_id"},
                BaseChatMessageHistory,
                ("static_session_id_chat_1000", "session_id"),
            ),
        ],
    )
    def test_get_memory_session(self, task, config, cls, expected):
        """Test various scope configurations."""
        callback_manager = MagicMock(spec=IxCallbackManager)
        callback_manager.task = task
        callback_manager.chat_id = "1000"
        callback_manager.agent_id = "1001"
        callback_manager.task_id = "1002"
        callback_manager.user_id = "1003"

        result = get_memory_session(config, callback_manager, cls)
        assert result == expected

    def test_parse_scope_unsupported_scope(self, mock_callback_manager):
        config = {
            "scope": "unsupported_scope",
            "session_id": "123",
            "session_id_key": "session_id",
        }
        cls = BaseChatMessageHistory
        with pytest.raises(ValueError) as excinfo:
            get_memory_session(config, mock_callback_manager, cls)
        assert "unknown scope" in str(excinfo.value)


class TestLoadChain:
    def test_load_chain(self):
        pass
