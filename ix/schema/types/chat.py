import logging

import graphene
from graphene_django import DjangoObjectType

from ix.chat.models import Chat

logger = logging.getLogger(__name__)


class ChatType(DjangoObjectType):
    class Meta:
        model = Chat
        fields = "__all__"


class Query(graphene.ObjectType):
    chat = graphene.Field(ChatType, id=graphene.UUID(required=True))
    chats = graphene.List(ChatType)

    def resolve_chat(self, info, id):
        return Chat.objects.get(pk=id)

    def resolve_chats(self, info):
        return Chat.objects.all()
