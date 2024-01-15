import pytest
from langchain_core.messages import AIMessage

from ix.chains.loaders.core import ainit_chain_flow
from ix.chains.models import Chain
from ix.conftest import aload_fixture


@pytest.mark.openai_api
@pytest.mark.django_db
class TestKnowledge:
    """
    Tests for Knowledge agent.
    """

    async def test_knowledge_flow(self, anode_types, aix_context):
        """test loading the knowledge agent"""

        await aload_fixture("agent/knowledge")
        chain = await Chain.objects.aget(agent__alias="knowledge")

        # init flow
        runnable = await ainit_chain_flow(chain, context=aix_context)

        output = await runnable.ainvoke(input={"user_input": "test"})
        assert isinstance(output, AIMessage)
