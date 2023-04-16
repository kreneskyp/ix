import logging
from graphene_django import DjangoObjectType
from ix.task_log.models import Agent


logger = logging.getLogger(__name__)


class AgentType(DjangoObjectType):
    class Meta:
        model = Agent
        fields = "__all__"
