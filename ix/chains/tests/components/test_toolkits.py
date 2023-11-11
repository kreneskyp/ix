import pytest
from langchain.agents import AgentExecutor
from langchain.agents.agent_toolkits import FileManagementToolkit

from ix.chains.fixture_src.toolkit import FILE_MANAGEMENT_TOOLKIT_CLASS_PATH
from ix.chains.llm_chain import LLMChain
from ix.chains.tests.mock_configs import PROMPT_CHAT
from ix.chains.tests.test_config_loader import OPENAI_LLM

FILESYSTEM_TOOLKIT = {
    "class_path": FILE_MANAGEMENT_TOOLKIT_CLASS_PATH,
    "config": {
        "root_dir": "/var/app/workdir",
    },
}

AGENT_WITH_TOOLKIT = {
    "class_path": "ix.chains.loaders.agents.initialize_openai_functions",
    "config": {"llm": OPENAI_LLM, "tools": [FILESYSTEM_TOOLKIT]},
}

LLM_CHAIN = {
    "class_path": "ix.chains.llm_chain.LLMChain",
    "config": {
        "prompt": PROMPT_CHAT,
        "llm": OPENAI_LLM,
        "functions": [FILESYSTEM_TOOLKIT],
    },
}


@pytest.mark.django_db
class TestFileManagementToolkit:
    async def test_load(self, aload_chain):
        component = await aload_chain(FILESYSTEM_TOOLKIT)
        assert isinstance(component, FileManagementToolkit)


@pytest.mark.django_db
class TestToolkitIntegrations:
    async def test_load_chain_functions(self, aload_chain):
        component = await aload_chain(LLM_CHAIN)
        assert isinstance(component, LLMChain)

        # chain doesn't unpack tools until load_functions is called
        assert len(component.functions) == 1
        assert isinstance(component.functions[0], FileManagementToolkit)
        assert len(component.llm_kwargs.get("functions", [])) == 7

    async def test_load_agent_toolkit(self, aload_chain):
        component = await aload_chain(AGENT_WITH_TOOLKIT)
        assert isinstance(component, AgentExecutor)
        assert len(component.tools) == 7
