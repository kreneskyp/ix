import graphene
import logging
from django.db.models import Q
from graphene.types.generic import GenericScalar
from graphene_django import DjangoObjectType
from ix.chains.models import Chain, ChainNode, ChainEdge, NodeType
from ix.utils.exceptions import catch_and_print_traceback


logger = logging.getLogger(__name__)


class ChainType(DjangoObjectType):
    class Meta:
        model = Chain
        fields = "__all__"


class ConnectorType(graphene.ObjectType):
    key = graphene.String()
    type = graphene.String()
    source_type = graphene.String()
    multiple = graphene.Boolean(default_value=False)


class NodeTypeType(DjangoObjectType):
    connectors = graphene.List(ConnectorType)
    fields = GenericScalar()

    class Meta:
        model = NodeType
        fields = "__all__"


class PositionType(graphene.ObjectType):
    x = graphene.Float()
    y = graphene.Float()


class ChainNodeType(DjangoObjectType):
    config = GenericScalar()
    position = graphene.Field(PositionType)

    class Meta:
        model = ChainNode
        fields = "__all__"


class ChainEdgeType(DjangoObjectType):
    input_map = GenericScalar()

    class Meta:
        model = ChainEdge
        fields = "__all__"

    source = graphene.Field(ChainNodeType)
    target = graphene.Field(ChainNodeType)


class ChainWithGraphType(graphene.ObjectType):
    chain = graphene.Field(ChainType)
    nodes = graphene.List(ChainNodeType)
    edges = graphene.List(ChainEdgeType)


class Query(object):
    chain = graphene.Field(ChainType, id=graphene.UUID(required=True))
    chains = graphene.List(ChainType)
    graph = graphene.Field(ChainWithGraphType, id=graphene.UUID(required=True))
    node_types = graphene.List(NodeTypeType)

    search_node_types = graphene.List(NodeTypeType, search=graphene.String())

    def resolve_chain(self, info, id):
        return Chain.objects.get(pk=id)

    def resolve_chains(self, info):
        return Chain.objects.all()

    @catch_and_print_traceback
    def resolve_graph(self, info, id):
        chain = Chain.objects.get(id=id)
        nodes = chain.nodes.all()
        edges = chain.edges.all()

        return ChainWithGraphType(chain=chain, nodes=nodes, edges=edges)

    def resolve_node_types(self, info):
        return NodeType.objects.all()

    def resolve_search_node_types(self, info, search, chat_id=None):
        # basic search for now, add pg_vector similarity search later
        return NodeType.objects.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(type__icontains=search)
            | Q(class_path__icontains=search)
        )
