from django.contrib import admin
from django.urls import path, re_path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from ix.server.views import index, status, langsmith

urlpatterns = [
    path("", index, name="index"),
    path("status/", status),
    path("admin/", admin.site.urls),
    path("task_log>/", include("ix.task_log.urls")),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
    re_path(r"^langsmith/(?P<run_id>[0-9a-f-]+)/$", langsmith, name="langsmith"),
    re_path(r".*", index, name="index"),
]
