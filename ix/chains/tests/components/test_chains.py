import pytest
from langchain.chains import SequentialChain

from ix.chains.fixture_src.openai_functions import OPENAPI_CHAIN_CLASS_PATH
from ix.chains.tests.test_config_loader import OPENAI_LLM

OPENAPI_CHAIN = {
    "class_path": OPENAPI_CHAIN_CLASS_PATH,
    "config": {
        "llm": OPENAI_LLM,
        "spec": "https://www.klarna.com/us/shopping/public/openai/v0/api-docs/",
    },
}


@pytest.mark.django_db
class TestOpenAPIChain:
    async def test_load(self, aload_chain):
        ix_node = await aload_chain(OPENAPI_CHAIN)
        component = ix_node.child
        assert isinstance(component, SequentialChain)
