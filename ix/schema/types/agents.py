import logging
import graphene
from ix.agents.models import Agent, Resource
from graphene_django import DjangoObjectType
from graphene.types.generic import GenericScalar


logger = logging.getLogger(__name__)


class AgentType(DjangoObjectType):
    class Meta:
        model = Agent
        fields = "__all__"

    config = GenericScalar()


class ResourceType(DjangoObjectType):
    class Meta:
        model = Resource
        fields = "__all__"


class Query(graphene.ObjectType):
    agent = graphene.Field(AgentType, id=graphene.ID(required=True))
    agents = graphene.List(AgentType)

    def resolve_agent(self, info, id):
        return Agent.objects.get(pk=id)

    def resolve_agents(self, info):
        return Agent.objects.all()
