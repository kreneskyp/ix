import logging
import graphene
from django.db.models import Q

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
    agent = graphene.Field(AgentType, id=graphene.UUID(required=True))
    agents = graphene.List(AgentType)
    search_agents = graphene.List(AgentType, search=graphene.String())

    def resolve_search_agents(self, info, search):
        # basic search for now, add pg_vector similarity search later
        return Agent.objects.filter(
            Q(name__icontains=search) | Q(alias__icontains=search)
        )

    def resolve_agent(self, info, id):
        return Agent.objects.get(pk=id)

    def resolve_agents(self, info):
        return Agent.objects.all()
