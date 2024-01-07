from langchain.chat_models.fireworks import ChatFireworks
from langchain.llms.fireworks import Fireworks
import pytest
from langchain.llms import Ollama
from langchain_mistralai import ChatMistralAI

from ix.chains.fixture_src.llm import (
    FIREWORKS_CHAT_LLM_CLASS_PATH,
    FIREWORKS_LLM_CLASS_PATH,
    OLLAMA_LLM_CLASS_PATH,
    MISTRAL_LLM_CLASS_PATH,
)
from ix.chains.tests.test_config_loader import unpack_chain_flow

OLLAMA_LLM = {
    "class_path": OLLAMA_LLM_CLASS_PATH,
    "config": {"model": "llama2"},
}


@pytest.mark.django_db
class TestOllama:
    async def test_aload(self, aload_chain):
        flow = await aload_chain(OLLAMA_LLM)
        component = unpack_chain_flow(flow)
        assert isinstance(component, Ollama)


FIREWORKS_LLM = {
    "class_path": FIREWORKS_LLM_CLASS_PATH,
    "config": {
        "model": "accounts/fireworks/models/llama-v2-7b-chat",
        "fireworks_api_key": "mock key",
    },
}

FIREWORKS_CHAT_LLM = {
    "class_path": FIREWORKS_CHAT_LLM_CLASS_PATH,
    "config": {
        "model": "accounts/fireworks/models/llama-v2-7b-chat",
        "fireworks_api_key": "mock key",
    },
}


@pytest.mark.django_db
class TestFireworks:
    async def test_aload(self, aload_chain, mock_config_secrets):
        config = await mock_config_secrets(FIREWORKS_LLM, ["fireworks_api_key"])
        flow = await aload_chain(config)
        component = unpack_chain_flow(flow)
        assert isinstance(component, Fireworks)


@pytest.mark.django_db
class TestFireworksChat:
    async def test_aload(self, aload_chain, mock_config_secrets):
        config = await mock_config_secrets(FIREWORKS_CHAT_LLM, ["fireworks_api_key"])
        flow = await aload_chain(config)
        component = unpack_chain_flow(flow)
        assert isinstance(component, ChatFireworks)


@pytest.mark.django_db
class TestMistralChat:
    CONFIG = {
        "class_path": MISTRAL_LLM_CLASS_PATH,
        "config": {
            "model": "mistral-small",
            "mistral_api_key": "mock key",
        },
    }

    async def test_aload(self, aload_chain, mock_config_secrets):
        config = await mock_config_secrets(self.CONFIG, ["mistral_api_key"])
        ix_node = await aload_chain(config)
        component = ix_node.child
        assert isinstance(component, ChatMistralAI)
