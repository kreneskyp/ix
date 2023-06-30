from unittest.mock import MagicMock

import pytest

from ix.chains.llm_chain import LLMChain
from ix.memory.artifacts import ArtifactMemory
from ix.task_log.tests.fake import afake_artifact, afake_task

ARTIFACT_MEMORY = {
    "class_path": "ix.memory.artifacts.ArtifactMemory",
    "config": {
        "load_artifact": True,
    },
}


TASK_WITH_ARTIFACT_MEMORY = {
    "class_path": "ix.chains.tool_chain.LLMToolChain",
    "config": {
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
            "config": {"verbose": True},
        },
        "memory": ARTIFACT_MEMORY,
        "prompt": {
            "class_path": "langchain.prompts.chat.ChatPromptTemplate",
            "config": {
                "messages": [
                    {
                        "role": "system",
                        "template": "You are {name}! Answer a question about artifacts {related_artifacts}",
                        "input_variables": ["name", "related_artifacts"],
                    },
                ],
            },
        },
    },
}


@pytest.mark.django_db
class TestArtifactMemory:
    async def test_llm_integration(self, atask, aload_chain, mock_openai):
        """
        Test memory class when integrated with LLMChain. Tests that langchain
        will detect the memory variables and include them when rendering the prompt.
        """

        # configure mock
        mock_openai.__dict__["completion_with_retry"] = MagicMock(
            return_value=mock_openai.get_mock_content()
        )

        # create chain
        chain = await aload_chain(TASK_WITH_ARTIFACT_MEMORY)
        assert isinstance(chain, LLMChain)
        assert isinstance(chain.memory, ArtifactMemory)

        # verify memory isn't in input_keys. If it's in input_keys, it will be
        # required as an input by Sequence.
        assert chain.input_keys == ["name"]

        # run
        artifact1 = await afake_artifact(task=atask, key="test_artifact_1")
        await chain.arun(name="tester", artifact_keys=["test_artifact_1"])

        # assert artifact was used in prompt
        mock_openai.acompletion_with_retry.assert_called_once()
        message = mock_openai.acompletion_with_retry.call_args_list[0].kwargs[
            "messages"
        ][0]
        assert artifact1.as_memory_text() in message["content"]

    async def test_defaults(self, aclean_artifacts, aload_chain):
        instance = await aload_chain(ARTIFACT_MEMORY)
        assert isinstance(instance, ArtifactMemory)

        # test memory variables
        assert instance.memory_variables == ["related_artifacts"]

    async def test_load_memory(self, atask, aload_chain):
        """
        Test various scenarios for loading memory variables.
        """
        instance = await aload_chain(ARTIFACT_MEMORY)
        artifact1 = await afake_artifact(task=atask, key="test_artifact_1")
        artifact2 = await afake_artifact(task=atask, key="test_artifact_2")

        # test no artifact_keys
        result1 = instance.load_memory_variables(dict())
        assert result1 == {"related_artifacts": ""}

        # test empty artifact_keys
        result1 = instance.load_memory_variables(dict(artifact_keys=[]))
        assert result1 == {"related_artifacts": ""}

        # test one artifact_key
        inputs = dict(artifact_keys=["test_artifact_1"])
        result2 = instance.load_memory_variables(inputs=inputs)
        assert "REFERENCED ARTIFACTS:" in result2["related_artifacts"]
        assert artifact1.as_memory_text() in result2["related_artifacts"]
        assert artifact2.as_memory_text() not in result2["related_artifacts"]

        # test one artifact_key
        inputs = dict(artifact_keys=["test_artifact_1", "test_artifact_2"])
        result3 = instance.load_memory_variables(inputs=inputs)
        assert "REFERENCED ARTIFACTS:" in result3["related_artifacts"]
        assert artifact1.as_memory_text() in result3["related_artifacts"]
        assert artifact2.as_memory_text() in result3["related_artifacts"]

        # test unknown artifact_key
        # hax: this won't raise an error of any kind now, but it's worth considering
        #      how to handle this better in the future.
        inputs = dict(artifact_keys=["test_artifact_does_not_exist"])
        result4 = instance.load_memory_variables(inputs=inputs)
        assert result4 == {"related_artifacts": ""}

    def test_mapped_keys(self):
        """Test mapping config input/outputs"""
        pass

    async def test_scope(self, aclean_artifacts, atask, aload_chain):
        # artifact from another chat
        unrelated_task = await afake_task()
        afake_artifact(task=unrelated_task, key="test_artifact_3")

        # none of the excluded artifacts should be included in the memory
        instance = await aload_chain(ARTIFACT_MEMORY)
        inputs = dict(artifact_keys=["test_artifact_3"])
        result1 = instance.load_memory_variables(inputs=inputs)
        assert result1 == {"related_artifacts": ""}
