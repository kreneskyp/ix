import pytest

from ix.chains.fixture_src.flow import CHAIN_REF_CLASS_PATH
from ix.chains.loaders.context import IxContext
from ix.chains.models import Chain
from ix.chains.tests.fake import (
    afake_chain,
    afake_root,
    afake_chain_node,
    afake_chain_edge,
)
from ix.conftest import aload_fixture
from ix.runnable.ix import IxNode


@pytest.mark.django_db
class TestRunnableReference:
    """Tests using a chain reference to load a chain in part of another chain."""

    async def test_init(
        self, aix_context: IxContext, anode_types, mock_openai_streaming
    ):
        # chain to embed
        await aload_fixture("agent/pirate")
        to_embed = await Chain.objects.aget(agent__alias="pirate")

        # parent chain
        chain = await afake_chain()
        root = await afake_root(chain=chain)
        chain_ref = await afake_chain_node(
            chain=chain,
            config={
                "class_path": CHAIN_REF_CLASS_PATH,
                "config": {
                    "chain_id": str(to_embed.id),
                },
            },
        )
        await afake_chain_edge(
            chain=chain,
            source=root,
            target=chain_ref,
            source_key="inputs",
            target_key="in",
        )

        # load the chain
        runnable = await chain.aload_chain(aix_context)

        # run the chain
        result = await runnable.ainvoke(
            {
                "user_input": "hello",
                "artifact_ids": [],
            }
        )
        assert result == {
            "chat_output": {
                "additional_kwargs": {},
                "content": "mock llm response",
                "example": False,
                "type": "ai",
            },
            "user_input": "hello",
        }

        # Chain ref should be wrapped in an IxNode that captures the embedded
        # chain as a single runnable.
        assert isinstance(runnable, IxNode)
        assert runnable.node_id == chain_ref.id
