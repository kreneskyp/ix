import pytest
from httpx import AsyncClient

from ix.api.chains.endpoints import create_chain_chat
from ix.chat.models import Chat
from ix.server.fast_api import app
from ix.task_log.tests.fake import (
    afake_chain,
)
from ix.ix_users.tests.fake import afake_user


@pytest.mark.django_db
class TestEditorChat:
    async def test_get_chat(self, anode_types):
        """Test getting test chat for a chain"""
        # Create a chain to update
        await afake_user()
        chain = await afake_chain()
        chat = await create_chain_chat(chain)

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/chains/{chain.id}/chat")

        assert response.status_code == 200, response.content
        response = response.json()
        assert str(chat.id) == response["id"]

    async def test_get_chat_404(self, anode_types):
        """Test chat is created if it does not exist"""
        # Create a chain to update
        await afake_user()
        chain = await afake_chain()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/chains/{chain.id}/chat")

        assert response.status_code == 200, response.content
        response = response.json()
        assert response["id"]
        assert await Chat.objects.filter(id=response["id"]).aexists()
