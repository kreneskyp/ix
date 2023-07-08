import logging
import graphene
from django.db.models import Q
from graphene.types.generic import GenericScalar

from ix.chains.models import ChainNode, Chain, ChainEdge, NodeType
from ix.schema.types.chains import ChainNodeType, ChainEdgeType, ChainType
from ix.schema.utils import handle_exceptions

logger = logging.getLogger(__name__)


class ChainInput(graphene.InputObjectType):
    id = graphene.UUID()
    name = graphene.String()
    description = graphene.String()


class UpdateChainMutation(graphene.Mutation):
    class Arguments:
        data = ChainInput(required=True)

    chain = graphene.Field(ChainType)

    @staticmethod
    @handle_exceptions
    def mutate(root, info, data):
        chain = None
        if "id" in data:
            try:
                chain = Chain.objects.get(id=data["id"])
            except Chain.DoesNotExist:
                pass

        if chain:
            for field, value in data.items():
                setattr(chain, field, value)
            chain.save()
        else:
            chain = Chain.objects.create(**data)
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


class SetChainRootMutation(graphene.Mutation):
    class Arguments:
        chain_id = graphene.UUID(required=True)
        node_id = graphene.UUID(required=False)

    old = graphene.Field(ChainNodeType, required=False)
    root = graphene.Field(ChainNodeType, required=False)

    @staticmethod
    def mutate(root, info, chain_id, node_id=None):
        try:
            old_root = ChainNode.objects.get(chain_id=chain_id, root=True)
            old_root.root = False
            old_root.save(update_fields=["root"])
        except ChainNode.DoesNotExist:
            old_root = None

        if node_id:
            node = ChainNode.objects.get(id=node_id)
            node.root = True
            node.save(update_fields=["root"])
        else:
            node = None

        return SetChainRootMutation(old=old_root, root=node)


class AddChainNodeMutation(graphene.Mutation):
    class Arguments:
        data = ChainNodeInput(required=True)

    node = graphene.Field(ChainNodeType)

    @staticmethod
    def mutate(root, info, data):
        # create the chain if it isn't given
        if not data.get("chain_id", None):
            chain = Chain.objects.create(name="Unnamed", description="")
            data["chain_id"] = chain.id

        node_type = NodeType.objects.get(class_path=data["class_path"])
        node = ChainNode.objects.create(node_type=node_type, **data)
        return AddChainNodeMutation(node=node)


class UpdateChainNodeMutation(graphene.Mutation):
    class Arguments:
        data = ChainNodeInput(required=True)

    node = graphene.Field(ChainNodeType)

    @staticmethod
    def mutate(root, info, data):
        # don't allow updating the chain
        data.pop("chain_id", None)

        # convert field types:
        #  - list: comma separated string to list
        node = ChainNode.objects.get(id=data["id"])
        field_map = {field["name"]: field for field in node.node_type.fields}
        config = data.get("config", {})
        for key, value in config.items():
            field = field_map[key]
            if field["type"] == "list":
                if isinstance(value, str):
                    config[key] = [slice.strip() for slice in value.split(",")]

        for key, value in data.items():
            setattr(node, key, value)
        node.save()
        return UpdateChainNodeMutation(node=node)


class ChainNodePositionInput(graphene.InputObjectType):
    id = graphene.UUID()
    position = PositionInput()


class UpdateChainNodePositionMutation(graphene.Mutation):
    class Arguments:
        data = ChainNodePositionInput(required=True)

    node = graphene.Field(ChainNodeType)

    @staticmethod
    def mutate(root, info, data):
        # don't allow updating the chain
        data.pop("chain_id", None)

        node = ChainNode.objects.get(id=data["id"])
        node.position = data["position"]
        node.save(update_fields=["position"])
        return UpdateChainNodeMutation(node=node)


class DeleteChainNodeMutation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    node = graphene.Field(ChainNodeType, required=False)
    edges = graphene.List(ChainEdgeType, required=False)

    @staticmethod
    def mutate(root, info, id):
        try:
            node = ChainNode.objects.get(id=id)
        except ChainNode.DoesNotExist:
            # ignore if it doesn't exist since desired state is achieved
            node = None
            edges = None

        if node:
            # delete all edges that reference this node
            query = ChainEdge.objects.filter(Q(source_id=id) | Q(target_id=id))
            edges = list(query)
            query.delete()
            ChainNode.objects.filter(id=id).delete()

        return DeleteChainNodeMutation(node=node, edges=edges)


class ChainEdgeInput(graphene.InputObjectType):
    id = graphene.UUID()
    source_id = graphene.UUID(required=True)
    target_id = graphene.UUID(required=True)
    key = graphene.String()
    chain_id = graphene.UUID()
    relation = graphene.String(choices=["LINK", "PROP"])
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

    edge = graphene.Field(ChainEdgeType)

    @staticmethod
    def mutate(root, info, id):
        try:
            edge = ChainEdge.objects.get(id=id)
        except ChainEdge.DoesNotExist:
            # ignore if it doesn't exist since desired state is achieved
            edge = None

        if edge:
            ChainEdge.objects.get(id=id).delete()

        return DeleteChainEdgeMutation(edge=edge)


class Mutation(graphene.ObjectType):
    update_chain = UpdateChainMutation.Field()
    set_chain_root = SetChainRootMutation.Field()
    add_chain_node = AddChainNodeMutation.Field()
    update_chain_node = UpdateChainNodeMutation.Field()
    update_chain_node_position = UpdateChainNodePositionMutation.Field()
    delete_chain_node = DeleteChainNodeMutation.Field()
    add_chain_edge = AddChainEdgeMutation.Field()
    update_chain_edge = UpdateChainEdgeMutation.Field()
    delete_chain_edge = DeleteChainEdgeMutation.Field()


schema = graphene.Schema(mutation=Mutation)
