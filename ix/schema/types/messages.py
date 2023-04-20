import logging
from graphene.types.generic import GenericScalar
from graphene_django import DjangoObjectType

from ix.task_log.models import TaskLogMessage


logger = logging.getLogger(__name__)


class TaskLogMessageType(DjangoObjectType):
    class Meta:
        model = TaskLogMessage
        fields = "__all__"

    content = GenericScalar()
