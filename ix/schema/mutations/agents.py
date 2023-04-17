import graphene
from ix.agents.models import Agent, Resource
from ix.schema.types.agents import AgentType
from ix.schema.types.agents import ResourceType

from graphene.types.generic import GenericScalar


class AgentInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()
    purpose = graphene.String()
    model = graphene.String()
    system_prompt = graphene.String()
    commands = graphene.JSONString()
    config = GenericScalar()


class CreateAgentMutation(graphene.Mutation):
    agent = graphene.Field(AgentType)

    class Arguments:
        input = AgentInput(required=True)

    def mutate(self, info, input):
        agent = Agent.objects.create(
            name=input.name,
            model=input.model,
            system_prompt=input.system_prompt,
            commands=input.commands,
        )
        return CreateAgentMutation(agent=agent)


class UpdateAgentMutation(graphene.Mutation):
    agent = graphene.Field(AgentType)

    class Arguments:
        input = AgentInput(required=True)

    def mutate(self, info, input):
        agent = Agent.objects.get(pk=input.id)
        for key, value in input.items():
            if value is not None:
                setattr(agent, key, value)
        agent.save()
        return UpdateAgentMutation(agent=agent)


class DeleteAgentMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        agent = Agent.objects.get(pk=id)
        agent.delete()
        return DeleteAgentMutation(success=True)


class ResourceInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()
    type = graphene.String()
    config = graphene.JSONString()


class CreateResourceMutation(graphene.Mutation):
    resource = graphene.Field(ResourceType)

    class Arguments:
        input = ResourceInput(required=True)

    def mutate(self, info, input):
        resource = Resource.objects.create(
            name=input.name, type=input.type, config=input.config
        )
        return CreateResourceMutation(resource=resource)


class UpdateResourceMutation(graphene.Mutation):
    resource = graphene.Field(ResourceType)

    class Arguments:
        input = ResourceInput(required=True)

    def mutate(self, info, input):
        resource = Resource.objects.get(pk=input.id)
        for key, value in input.items():
            if value is not None:
                setattr(resource, key, value)
        resource.save()
        return UpdateResourceMutation(resource=resource)


class DeleteResourceMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        resource = Resource.objects.get(pk=id)
        resource.delete()
        return DeleteResourceMutation(success=True)


class Mutation(graphene.ObjectType):
    create_agent = CreateAgentMutation.Field()
    update_agent = UpdateAgentMutation.Field()
    delete_agent = DeleteAgentMutation.Field()
    create_resource = CreateResourceMutation.Field()
    update_resource = UpdateResourceMutation.Field()
    delete_resource = DeleteResourceMutation.Field()
