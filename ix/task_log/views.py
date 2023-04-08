from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from .schema import schema

graphql_view = csrf_exempt(GraphQLView.as_view(schema=schema))
