import graphene
from graphene_django import DjangoObjectType
from .models import CodeObject, Relation, Invocation


class CodeObjectType(DjangoObjectType):
    superclass = graphene.Field(lambda: CodeObjectType)
    child_classes = graphene.List(lambda: CodeObjectType)
    invocations = graphene.List(lambda: InvocationType)
    invoked_by = graphene.List(lambda: InvocationType)

    class Meta:
        model = CodeObject
        fields = ("name", "type")

    def resolve_superclass(self, info):
        relation = Relation.objects.filter(
            child=self, parent__type=CodeObject.CLASS
        ).first()
        return relation.parent if relation else None

    def resolve_child_classes(self, info):
        return CodeObject.objects.filter(parents__parent=self, type=CodeObject.CLASS)

    def resolve_invocations(self, info):
        return self.invocations.all()

    def resolve_invoked_by(self, info):
        return self.invoked_by.all()


class InvocationType(DjangoObjectType):
    class Meta:
        model = Invocation
        fields = ("invoker", "invokee", "line_number")


class Query(graphene.ObjectType):
    get_class_with_methods = graphene.Field(
        CodeObjectType, class_path=graphene.String(required=True)
    )

    def resolve_get_class_with_methods(root, info, class_path):
        # Assuming class_path is unique
        code_object = CodeObject.objects.get(
            location__class_path=class_path, type=CodeObject.CLASS
        )
        return code_object


schema = graphene.Schema(query=Query)
