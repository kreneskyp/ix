import pytest
from graphene.test import Client
from ix.schema import schema
from ix.task_log.tests.fake import fake_chat, fake_artifact


ARTIFACT_SEARCH = """
   query SearchArtifactsQuery($search: String, $chatId: UUID!) {
    searchArtifacts(search: $search, chatId: $chatId) {
      id
      key
      name
      description
      artifactType
      storage
    }
  }
"""


@pytest.mark.django_db
class TestArtifactSearch:
    def test_artifact_search_name(self):
        """Test basic search by key"""
        chat = fake_chat()
        artifact1 = fake_artifact(name="artifact 1", key="artifact_1", task=chat.task)
        fake_artifact(name="artifact 2", key="artifact_2", task=chat.task)

        variables = {
            "chatId": str(chat.id),
            "search": "artifact_1",
        }

        client = Client(schema)
        response = client.execute(ARTIFACT_SEARCH, variables=variables)

        assert "errors" not in response
        assert len(response["data"]["searchArtifacts"]) == 1
        assert response["data"]["searchArtifacts"][0]["id"] == str(artifact1.id)

    def test_chat_required(self):
        """chat is a required field"""
        variables = {
            "search": "artifact_1",
        }

        client = Client(schema)
        response = client.execute(ARTIFACT_SEARCH, variables=variables)

        assert "errors" in response
        assert (
            response["errors"][0]["message"]
            == "Variable '$chatId' of required type 'UUID!' was not provided."
        )

    def test_chat_does_not_exist(self):
        """chat must exist"""
        variables = {
            "search": "artifact_1",
            "chatId": "00000000-0000-0000-0000-000000000000",
        }

        client = Client(schema)
        response = client.execute(ARTIFACT_SEARCH, variables=variables)

        assert "errors" in response
        assert response["errors"][0]["message"] == "Chat matching query does not exist."

    def test_duplicate_keys(self):
        """If there are multiple Artifacts with the same key, only the latest is returned"""
        chat = fake_chat()
        artifact1 = fake_artifact(name="artifact 1", key="artifact_1", task=chat.task)
        artifact2 = fake_artifact(name="artifact 2", key="artifact_1", task=chat.task)
        assert artifact2.created_at > artifact1.created_at

        variables = {
            "chatId": str(chat.id),
            "search": "artifact_1",
        }

        client = Client(schema)
        response = client.execute(ARTIFACT_SEARCH, variables=variables)

        assert "errors" not in response
        assert len(response["data"]["searchArtifacts"]) == 1
        assert response["data"]["searchArtifacts"][0]["id"] != str(artifact1.id)
        assert response["data"]["searchArtifacts"][0]["id"] == str(artifact2.id)

    def test_artifact_in_other_chat(self):
        """Only return artifacts from the chat specified"""
        chat1 = fake_chat(id="f0034449-f226-44b2-9036-ca49f7d2348e")
        chat2 = fake_chat(id="f0034449-f226-44b2-9036-ca49f7d2348a")
        fake_artifact(name="artifact 1", key="artifact_1", task=chat2.task)

        variables = {
            "chatId": str(chat1.id),
            "search": "artifact_1",
        }

        client = Client(schema)
        response = client.execute(ARTIFACT_SEARCH, variables=variables)

        assert "errors" not in response
        assert len(response["data"]["searchArtifacts"]) == 0

    @pytest.mark.skip("user auth not implemented yet")
    def test_chat_is_not_users(self):
        """Raise a 403 if the user does not have access to the chat they are trying to search"""
        raise NotImplementedError
