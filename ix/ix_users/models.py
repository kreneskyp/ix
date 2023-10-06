from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group as DjangoGroup
from django.db import models
from django.db.models import Q, QuerySet


Group = DjangoGroup


class User(AbstractUser):
    pass


class OwnedModel(models.Model):
    """Mixin to provide consistent ownership fields and filtering for models."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True

    @staticmethod
    def filter_owners( user: User, queryset: QuerySet) -> QuerySet:
        """Filter a queryset to only include objects available to the given user:

        - Global objects with no owner
        - Objects owned by the user
        - Objects owned by a group the user is a member of

        Assumes they inherit from OwnedMixin.
        """

        # disable filtering for local deployments
        if not settings.OWNER_FILTERING:
            return queryset

        return queryset.filter(Q(user_id=None, group_id=None) | Q(user_id=user.id) | Q(group_id__users__id=user.id))