import pytest

from ix.chains.agent_interaction import DelegateToAgentChain
from ix.task_log.models import Task

DELEGATE_TO_AGENT_CHAIN = {
    "class_path": "ix.chains.agent_interaction.DelegateToAgentChain",
    "config": {
        "target_alias": "agent_1",
        "prompt": {
            "class_path": "langchain.prompts.chat.ChatPromptTemplate",
            "config": {
                "messages": [
                    {
                        "role": "system",
                        "template": "Write a sea shanty for user input: {user_input}.",
                        "input_variables": ["user_input"],
                    },
                ],
            },
        },
    },
}


DELEGATE_TO_AGENT_CHAIN_FILTER_INPUTS = {
    "class_path": "ix.chains.agent_interaction.DelegateToAgentChain",
    "config": {
        "target_alias": "agent_1",
        "delegate_inputs": ["user_input"],
        "prompt": {
            "class_path": "langchain.prompts.chat.ChatPromptTemplate",
            "config": {
                "messages": [
                    {
                        "role": "system",
                        "template": "Write a sea shanty for user input: {user_input}.",
                        "input_variables": ["user_input"],
                    },
                ],
            },
        },
    },
}


@pytest.fixture
def start_agent_loop(mocker):
    # mock start_agent_loop since the task is async and makes this test flaky
    yield mocker.patch("ix.chains.agent_interaction.start_agent_loop")


@pytest.mark.django_db
class TestDelegateToAgentChain:
    async def test_delegate_to_agent(
        self, aload_chain, aix_handler, achat, start_agent_loop
    ):
        """Verify that the chain will delegate to the agent"""
        chat = achat["chat"]
        task = await Task.objects.aget(id=chat.task_id)
        chain = await aload_chain(DELEGATE_TO_AGENT_CHAIN)
        assert isinstance(chain, DelegateToAgentChain)

        result = await chain.arun(
            chat_id=str(chat.id),
            user_input="test task delegation",
            extra_input="testing extra input",
            callbacks=[aix_handler],
        )
        assert result == "Delegating to @agent_1"
        assert start_agent_loop.delay.call_args_list[0].kwargs["user_id"] == str(
            task.user_id
        )
        assert start_agent_loop.delay.call_args_list[0].kwargs["inputs"] == {
            "chat_id": str(chat.id),
            "user_input": "System: Write a sea shanty for user input: test task delegation.",
            "extra_input": "testing extra input",
        }

    async def test_delegate_to_agent_summons_agents(
        self, aload_chain, aix_handler, achat, start_agent_loop
    ):
        """Verify that the chain will delegate to the agent"""
        chat = achat["chat"]
        chain = await aload_chain(DELEGATE_TO_AGENT_CHAIN)
        assert isinstance(chain, DelegateToAgentChain)

        # remove agents
        await chat.agents.all().adelete()
        assert await chat.agents.aexists() is False

        result = await chain.arun(
            chat_id=str(chat.id),
            user_input="test task delegation",
            callbacks=[aix_handler],
        )
        assert result == "Delegating to @agent_1"
        assert await chat.agents.filter(alias="agent_1").aexists()

    async def test_delegate_to_agent_filter_inputs(
        self, aload_chain, aix_handler, achat, start_agent_loop
    ):
        """Verify that the chain will delegate to the agent"""
        chat = achat["chat"]
        chain = await aload_chain(DELEGATE_TO_AGENT_CHAIN_FILTER_INPUTS)
        assert isinstance(chain, DelegateToAgentChain)

        result = await chain.arun(
            chat_id=str(chat.id),
            user_input="test task delegation",
            excluded_input="this input won't be passed to the agent",
            callbacks=[aix_handler],
        )
        assert result == "Delegating to @agent_1"
        start_agent_loop.delay.assert_called_once()
        assert start_agent_loop.delay.call_args_list[0].kwargs["inputs"] == {
            "chat_id": str(chat.id),
            "user_input": "System: Write a sea shanty for user input: test task delegation.",
        }
