import pytest
from langchain_community.embeddings import (
    HuggingFaceEmbeddings,
    HuggingFaceBgeEmbeddings,
    HuggingFaceInstructEmbeddings,
    HuggingFaceHubEmbeddings,
    HuggingFaceInferenceAPIEmbeddings,
)

from ix.chains.fixture_src.embeddings import (
    HUGGINGFACE_EMBEDDINGS_CLASS_PATH,
    HUGGINGFACE_INSTRUCT_EMBEDDINGS_CLASS_PATH,
    HUGGINGFACE_BGE_EMBEDDINGS_CLASS_PATH,
    HUGGINGFACE_INFERENCE_API_EMBEDDINGS_CLASS_PATH,
    HUGGINGFACE_HUB_EMBEDDINGS_CLASS_PATH,
)


@pytest.mark.skip(reason="dependencies not installed by default")
@pytest.mark.django_db
class TestHugggingFaceEmbeddings:
    """Smoke tests for HuggingFace Embeddings."""

    async def test_huggingface_embeddings(self, aload_chain):
        config = {
            "class_path": HUGGINGFACE_EMBEDDINGS_CLASS_PATH,
            "config": {},
        }

        component = await aload_chain(config)
        assert isinstance(component, HuggingFaceEmbeddings)

    async def test_huggingface_instruct_embeddings(self, aload_chain):
        config = {
            "class_path": HUGGINGFACE_INSTRUCT_EMBEDDINGS_CLASS_PATH,
            "config": {},
        }

        component = await aload_chain(config)
        assert isinstance(component, HuggingFaceInstructEmbeddings)

    async def test_huggingface_bge_embeddings(self, aload_chain):
        config = {
            "class_path": HUGGINGFACE_BGE_EMBEDDINGS_CLASS_PATH,
            "config": {},
        }

        component = await aload_chain(config)
        assert isinstance(component, HuggingFaceBgeEmbeddings)

    async def test_huggingface_inference_api_embeddings(
        self, aload_chain, mock_config_secrets
    ):
        config = {
            "class_path": HUGGINGFACE_INFERENCE_API_EMBEDDINGS_CLASS_PATH,
            "config": {
                "api_key": "fake_key",
            },
        }
        config = await mock_config_secrets(config, ["api_key"])

        component = await aload_chain(config)
        assert isinstance(component, HuggingFaceInferenceAPIEmbeddings)

    async def test_huggingface_hub_embeddings(self, aload_chain, mock_config_secrets):
        config = {
            "class_path": HUGGINGFACE_HUB_EMBEDDINGS_CLASS_PATH,
            "config": {
                "huggingfacehub_api_token": "fake_token",
            },
        }

        config = await mock_config_secrets(config, ["huggingfacehub_api_token"])
        component = await aload_chain(config)
        assert isinstance(component, HuggingFaceHubEmbeddings)
