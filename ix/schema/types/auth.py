import logging
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"
