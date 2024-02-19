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

    @classmethod
    def filtered_owners(cls, user: User, global_restricted=False) -> QuerySet:
        """Filter a queryset to only include objects available to the given user.
        Shortcut for `filter_owners(user, cls.objects.all())`

        Example:

        ```
        OwnedModel.filtered_owners(user)
        ```
        """
        queryset = cls.objects.all()
        return cls.filter_owners(user, queryset, global_restricted=global_restricted)

    @staticmethod
    def filter_owners(
        user: User, queryset: QuerySet, global_restricted=False, prefix=""
    ) -> QuerySet:
        """Filter a queryset to only include objects available to the given user:

        - Global objects with no owner (if global_restricted is False or user is not admin)
        - Objects owned by the user
        - Objects owned by a group the user is a member of

        Assumes they inherit from OwnedMixin.
        """

        # Disable filtering for local deployments
        if not settings.OWNER_FILTERING:
            return queryset

        if not user:
            return queryset.none()

        # Prepend prefix to field lookups if provided
        user_field = f"{prefix}user_id" if prefix else "user_id"
        group_field = f"{prefix}group__user" if prefix else "group__user"
        global_user_field = f"{prefix}user_id" if prefix else "user_id"
        global_group_field = f"{prefix}group_id" if prefix else "group_id"

        user_owned = Q(**{user_field: user.id})
        group_owned = Q(**{group_field: user})
        global_owned = Q(**{global_user_field: None, global_group_field: None})

        if global_restricted and not user.is_superuser:
            return queryset.exclude(global_owned).filter(user_owned | group_owned)
        else:
            return queryset.filter(user_owned | group_owned | global_owned)
