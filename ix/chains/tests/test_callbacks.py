import pytest
from django.db.models.signals import post_save

from ix.agents.models import Agent
from ix.chains.callbacks import IxHandler
from ix.chains.models import Chain
from ix.chains.tests.test_config_loader import unpack_chain_flow
from ix.schema.subscriptions import ChatMessageTokenSubscription
from ix.task_log.models import Task, TaskLogMessage

CHAIN_WITH_LLM = {
    "name": "test chain",
    "class_path": "ix.chains.llm_chain.LLMChain",
    "config": {
        "llm": {
            "class_path": "langchain_community.chat_models.ChatOpenAI",
            "config": {"streaming": True},
        },
        "prompt": {
            "class_path": "ix.runnable.prompt.ChatPrompt",
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


@pytest.mark.django_db
class TestIxHandler:
    async def test_stream(self, achat, aload_chain, mock_openai_streaming, mocker):
        await TaskLogMessage.objects.all().adelete()
        spy_broadcast = mocker.spy(ChatMessageTokenSubscription, "broadcast")
        saves = []

        def save_handler(sender, instance, created, **kwargs):
            if instance.content["type"] == "ASSISTANT":
                saves.append(
                    {
                        "text": instance.content["text"],
                        "stream": instance.content["stream"],
                    }
                )

        post_save.connect(save_handler, sender=TaskLogMessage)

        chat = achat["chat"]
        task = await Task.objects.aget(id=chat.task_id)
        chain = await Chain.objects.aget(id=task.chain_id)
        agent = await Agent.objects.aget(id=task.agent_id)

        handler = IxHandler(agent=agent, chain=chain, task=task)
        flow = await aload_chain(CHAIN_WITH_LLM)
        langchain_chain = unpack_chain_flow(flow)
        langchain_chain.llm.streaming = True
        assert langchain_chain.llm.streaming is True

        result = await langchain_chain.acall(
            inputs=dict(user_input="testing"), callbacks=[handler]
        )
        msg = await TaskLogMessage.objects.aget(
            task_id=task.id, content__type="ASSISTANT"
        )
        assert result == {"user_input": "testing", "text": "mock llm response"}

        # verify that placeholder was saved and then updated on completion
        assert len(saves) == 2
        assert saves[0]["stream"] is True
        assert saves[0]["text"] == ""
        assert saves[1]["stream"] is False
        assert saves[1]["text"] == "mock llm response"

        # verify django-channel publish calls
        for call in spy_broadcast.call_args_list:
            assert call.kwargs["group"] == f"stream_task_id_{task.id}"
        calls = spy_broadcast.call_args_list
        assert len(calls) == 5
        assert calls[0].kwargs["payload"] == {
            "msg_id": str(msg.id),
            "index": 1,
            "text": "mock",
        }
        assert calls[1].kwargs["payload"] == {
            "msg_id": str(msg.id),
            "index": 2,
            "text": " ",
        }
        assert calls[2].kwargs["payload"] == {
            "msg_id": str(msg.id),
            "index": 3,
            "text": "llm",
        }
        assert calls[3].kwargs["payload"] == {
            "msg_id": str(msg.id),
            "index": 4,
            "text": " ",
        }
        assert calls[4].kwargs["payload"] == {
            "msg_id": str(msg.id),
            "index": 5,
            "text": "response",
        }
