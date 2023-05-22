import logging
import graphene
from graphene import Field, Int
from graphene_django import DjangoObjectType

from ix.chat.models import Chat
from ix.utils.graphene.pagination import GenericPage

logger = logging.getLogger(__name__)


class ChatType(DjangoObjectType):
    class Meta:
        model = Chat
        fields = "__all__"


class ChatsPage(GenericPage):
    objects = graphene.List(ChatType)


class Query(graphene.ObjectType):
    chat = graphene.Field(ChatType, id=graphene.UUID(required=True))
    chats = graphene.List(ChatType)

    chat_page = Field(
        ChatsPage,
        limit=Int(default_value=10),
        offset=Int(default_value=0),
    )

    def resolve_chat_page(self, info, limit, offset):
        queryset = Chat.objects.all().order_by("-created_at")
        return ChatsPage.paginate(queryset, limit, offset)

    def resolve_chat(self, info, id):
        return Chat.objects.get(pk=id)

    def resolve_chats(self, info):
        return Chat.objects.all()
