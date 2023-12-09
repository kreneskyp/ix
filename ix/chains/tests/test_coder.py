import pytest

from ix.api.artifacts.types import Artifact
from ix.chains.models import Chain
from ix.conftest import aload_fixture


@pytest.mark.django_db
class TestFlowCoder:
    async def test_create_flow_coder(self, anode_types, aix_context, aix_handler):
        """Sanity check that fixture can be loaded and initialized"""
        await aload_fixture("agent/code2")
        chain = await Chain.objects.aget(agent__alias="code2")

        # init flow
        await chain.aload_chain(context=aix_context)

    @pytest.mark.openai_api
    async def test_invoke_flow_coder(self, anode_types, aix_context, aix_handler):
        """Test running coder flow"""
        await aload_fixture("agent/code2")
        chain = await Chain.objects.aget(agent__alias="code2")

        # init flow
        runnable = await chain.aload_chain(context=aix_context)

        result = await runnable.ainvoke(
            input={"user_input": "write a python fizzbuzz"},
            config={"callbacks": [aix_handler]},
        )
        assert isinstance(result, list)
        assert len(result) >= 1
        assert isinstance(result[0], Artifact)
