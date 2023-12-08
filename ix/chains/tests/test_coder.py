import pytest
from django.core.management import call_command
from langchain.chains import SequentialChain

from ix.chains.artifacts import SaveArtifact
from ix.chains.llm_chain import LLMChain
from ix.chains.management.commands.create_coder_v2 import CODER_V2_CHAIN
from ix.chains.models import Chain
from ix.chains.routing import MapSubchain
from ix.conftest import aload_fixture


@pytest.mark.django_db
class TestCreateCoder:
    def test_create_coder(self, mock_openai_key, ix_context):
        call_command("create_coder_v2")

        model_instance = Chain.objects.get(id=CODER_V2_CHAIN)
        chain = model_instance.load_chain(ix_context)

        # assert structure of main sequence
        assert isinstance(chain, SequentialChain)
        assert isinstance(chain.chains[0], LLMChain)
        assert isinstance(chain.chains[1], SaveArtifact)
        assert isinstance(chain.chains[2], MapSubchain)

        # assert structure of mapsubchain
        mapsubchain = chain.chains[2]
        assert isinstance(mapsubchain.chains[0], LLMChain)
        assert isinstance(mapsubchain.chains[1], SaveArtifact)

    async def test_create_coder2(self, anode_types, aix_context, aix_handler):
        await aload_fixture("agent/code2")
        chain = await Chain.objects.aget(agent__alias="code2")

        # init flow
        runnable = await chain.aload_chain(context=aix_context)

        from pprint import pprint

        pprint(runnable)

        # 0/0
        result = await runnable.ainvoke(
            input={"user_input": "write a python fizzbuzz"},
            config={"callbacks": [aix_handler]},
        )
        print()
        pprint(result)

        0 / 0
