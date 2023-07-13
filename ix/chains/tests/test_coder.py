import pytest
from django.core.management import call_command
from langchain.chains import SequentialChain

from ix.chains.artifacts import SaveArtifact
from ix.chains.llm_chain import LLMChain
from ix.chains.management.commands.create_coder_v2 import CODER_V2_CHAIN
from ix.chains.models import Chain
from ix.chains.routing import MapSubchain


@pytest.mark.django_db
@pytest.mark.usefixtures("node_types")
class TestCreateCoder:
    def test_create_coder(self, mock_callback_manager, mock_openai_key):
        call_command("create_coder_v2")

        model_instance = Chain.objects.get(id=CODER_V2_CHAIN)
        chain = model_instance.load_chain(mock_callback_manager)

        # assert structure of main sequence
        assert isinstance(chain, SequentialChain)
        assert isinstance(chain.chains[0], LLMChain)
        assert isinstance(chain.chains[1], SaveArtifact)
        assert isinstance(chain.chains[2], MapSubchain)

        # assert structure of mapsubchain
        mapsubchain = chain.chains[2]
        assert isinstance(mapsubchain.chains[0], LLMChain)
        assert isinstance(mapsubchain.chains[1], SaveArtifact)
