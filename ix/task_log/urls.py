from django.urls import path
from .views import graphql_view

urlpatterns = [
    path("graphql/", graphql_view, name="graphql"),
]
