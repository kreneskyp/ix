import logging
import graphene
from graphene.types.generic import GenericScalar

from ix.chains.models import ChainNode, Chain, ChainEdge
from ix.schema.types.chains import ChainNodeType, ChainEdgeType

logger = logging.getLogger(__name__)


class ChainInput(graphene.InputObjectType):
    id = graphene.UUID()
    name = graphene.String()
    description = graphene.String()


class UpdateChainMutation(graphene.Mutation):
    class Arguments:
        data = ChainInput(required=True)

    chain = graphene.Field(ChainNodeType)

    @staticmethod
    def mutate(root, info, data):
        chain = Chain.objects.pop(id=data["id"])

        for field, value in data.items():
            setattr(chain, field, value)
        chain.save()
        return UpdateChainMutation(chain=chain)


class PositionInput(graphene.InputObjectType):
    x = graphene.Float()
    y = graphene.Float()


class ChainNodeInput(graphene.InputObjectType):
    id = graphene.UUID()
    chain_id = graphene.UUID()
    class_path = graphene.String(required=True)
    config = GenericScalar()
    name = graphene.String()
    description = graphene.String()
    position = PositionInput()
    node_type = graphene.String(required=False)


class AddChainNodeMutation(graphene.Mutation):
    class Arguments:
        data = ChainNodeInput(required=True)

    node = graphene.Field(ChainNodeType)

    @staticmethod
    def mutate(root, info, data):
        # create the chain if it isn't given
        data.pop("node_type", None)

        if not data.get("chain_id", None):
            chain = Chain.objects.create(name="Unnamed", description="")
            data["chain_id"] = chain.id

        node = ChainNode.objects.create(**data)
        return AddChainNodeMutation(node=node)


class UpdateChainNodeMutation(graphene.Mutation):
    class Arguments:
        data = ChainNodeInput(required=True)

    node = graphene.Field(ChainNodeType)

    @staticmethod
    def mutate(root, info, data):
        # don't allow updating the chain
        data.pop("chain_id", None)

        node = ChainNode.objects.get(id=data["id"])
        for field, value in data.items():
            setattr(node, field, value)
        node.save()
        return UpdateChainNodeMutation(node=node)


class DeleteChainNodeMutation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    id = graphene.UUID()

    @staticmethod
    def mutate(root, info, id):
        ChainNode.objects.get(id=id).delete()
        return DeleteChainNodeMutation(id=id)


class ChainEdgeInput(graphene.InputObjectType):
    id = graphene.UUID()
    source_id = graphene.UUID(required=True)
    target_id = graphene.UUID(required=True)
    key = graphene.String()
    chain_id = graphene.UUID()
    input_map = GenericScalar()


class AddChainEdgeMutation(graphene.Mutation):
    class Arguments:
        data = ChainEdgeInput(required=True)

    edge = graphene.Field(ChainEdgeType)

    @staticmethod
    def mutate(root, info, data):
        edge = ChainEdge.objects.create(**data)
        return AddChainEdgeMutation(edge=edge)


class UpdateChainEdgeMutation(graphene.Mutation):
    class Arguments:
        data = ChainEdgeInput(required=True)

    edge = graphene.Field(ChainEdgeType)

    @staticmethod
    def mutate(root, info, data):
        # don't allow updating the chain
        data.pop("chain_id", None)

        edge = ChainEdge.objects.get(id=data["id"])
        for field, value in data.items():
            setattr(edge, field, value)
        edge.save()
        return UpdateChainEdgeMutation(edge=edge)


class DeleteChainEdgeMutation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    id = graphene.UUID()

    @staticmethod
    def mutate(root, info, id):
        ChainEdge.objects.get(id=id).delete()
        return DeleteChainEdgeMutation(id=id)


class Mutation(graphene.ObjectType):
    update_chain = UpdateChainMutation.Field()
    add_chain_node = AddChainNodeMutation.Field()
    update_chain_node = UpdateChainNodeMutation.Field()
    delete_chain_node = DeleteChainNodeMutation.Field()
    add_chain_edge = AddChainEdgeMutation.Field()
    update_chain_edge = UpdateChainEdgeMutation.Field()
    delete_chain_edge = DeleteChainEdgeMutation.Field()


schema = graphene.Schema(mutation=Mutation)
