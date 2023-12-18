import base64
from pathlib import Path

import pytest
import pytest_asyncio
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.runnables import RunnableSequence

from ix.chains.loaders.context import IxContext
from ix.chains.loaders.prompts import create_message
from ix.chains.models import Chain
from ix.conftest import aload_fixture
from ix.runnable.prompt import MultiModalChatPrompt
from ix.task_log.tests.fake import afake_artifact

TEST_MESSAGES = [
    {
        "role": "system",
        "template": "You are a test construct",
    },
    {
        "role": "assistant",
        "template": "I am a test construct",
    },
    {
        "role": "user",
        "template": "{user_input}",
    },
]


TEST_IMAGE = Path("/var/app/ix_350.png")


@pytest.fixture
def mock_image():
    with open(TEST_IMAGE, "rb") as f:
        image = f.read()

    as_base_64 = base64.b64encode(image).decode("utf-8")
    base_64_url = f"data:image/png;base64,{as_base_64}"

    yield {
        "path": TEST_IMAGE,
        "base64": base_64_url,
    }


class TestMultiModalChatPrompt:
    async def test_invoke(self):
        messages = [create_message(message) for message in TEST_MESSAGES]
        template = MultiModalChatPrompt(
            messages=messages, input_variables=["user_input"]
        )
        response = await template.ainvoke(input={"user_input": "Hello, world"})

        from pprint import pprint

        assert response == ChatPromptValue(
            messages=[
                SystemMessage(content="You are a test construct"),
                AIMessage(content="I am a test construct"),
                HumanMessage(content="Hello, world"),
            ]
        )

        # test with images
        response2 = await template.ainvoke(
            input={
                "user_input": "Hello, world",
                "images": ["https://0.0.0.0:8000/icon.jpeg"],
            }
        )
        assert response2 == ChatPromptValue(
            messages=[
                SystemMessage(content="You are a test construct"),
                AIMessage(content="I am a test construct"),
                HumanMessage(content="Hello, world"),
                HumanMessage(
                    content=[
                        {
                            "type": "image_url",
                            "image_url": {"url": "https://0.0.0.0:8000/icon.jpeg"},
                        }
                    ]
                ),
            ]
        )

    @pytest.mark.openai_api
    async def test_multi_modal_request(self, mock_image):
        """Real request to OpenAI with multi-modal prompt"""

        message = {
            "role": "user",
            "template": "what does this image contain?",
        }
        messages = [create_message(message)]
        template = MultiModalChatPrompt(messages=messages)

        chain = template | ChatOpenAI(
            model_name="gpt-4-vision-preview", max_tokens=3000
        )
        response = await chain.ainvoke(
            input={"user_input": "Hello, world", "images": [mock_image["base64"]]}
        )
        assert isinstance(response, AIMessage)


@pytest.mark.django_db
class TestVisionAgent:
    @pytest_asyncio.fixture()
    async def vision_runnable(
        self, anode_types, aix_context: IxContext, mock_filesystem, mock_openai_key
    ):
        await aload_fixture("agent/vision")
        chain = await Chain.objects.aget(agent__alias="vision")
        runnable = await chain.aload_chain(aix_context)
        yield runnable

    async def test_load(self, vision_runnable):
        assert isinstance(vision_runnable, RunnableSequence)

    @pytest.mark.openai_api
    async def test_invoke(
        self, vision_runnable, aix_context: IxContext, mock_filesystem
    ):
        # setup artifact
        with open(TEST_IMAGE, "rb") as f:
            image = f.read()
            mock_filesystem.write_file("ix_350.png", image)

        artifact = await afake_artifact(
            task_id=aix_context.task_id,
            key="test",
            artifact_type="image",
            name="ix logo",
            description="IX Logo 350px size",
            storage={
                "backend": "filesystem",
                "id": "ix_350.png",
            },
        )

        response = await vision_runnable.ainvoke(
            input={
                "user_input": "What is in this image?",
                "artifact_ids": [str(artifact.id)],
            }
        )
        # TODO: implement assertion
        assert response == {}
