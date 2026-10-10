import pytest
from langchain.llms import Ollama

from ix.chains.fixture_src.llm import OLLAMA_LLM_CLASS_PATH

OLLAMA_LLM = {
    "class_path": OLLAMA_LLM_CLASS_PATH,
    "config": {"model": "llama2"},
}


@pytest.mark.django_db
class TestOllama:
    async def test_load_search(self, aload_chain):
        component = await aload_chain(OLLAMA_LLM)
        assert isinstance(component, Ollama)
