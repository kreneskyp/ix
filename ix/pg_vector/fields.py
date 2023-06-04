from typing import List

from django.db.models import Func
from django.contrib.postgres.fields import ArrayField
from django.db import models


class VectorField(ArrayField):
    """
    A custom Django field for storing vectors in PostgreSQL using the `pgvector` extension.
    """

    OPEN_AI = 1536

    def db_type(self, connection):
        """
        Returns the database type for this field.
        """
        return "vector(%s)" % self.size

    def __init__(self, *args, size=OPEN_AI, **kwargs):
        """
        Initializes the field with the given size (dimensionality of the vector),
        and by default allows null values.
        """
        self.size = size
        kwargs.setdefault("null", True)
        base_field = kwargs.pop("base_field", models.FloatField())
        super().__init__(base_field=base_field, size=size, *args, **kwargs)

    def deconstruct(self):
        """
        Deconstructs the field for migrations.
        """
        name, path, args, kwargs = super().deconstruct()  # pragma: no cover
        kwargs["size"] = self.size  # pragma: no cover
        return name, path, args, kwargs  # pragma: no cover

    def clone(self):
        """
        Creates a copy of this field for migrations.
        """
        return self.__class__(name=self.name, size=self.size)

    def get_internal_type(self):
        """
        Returns the name of this field for migrations.
        """
        return "VectorField"

    def from_db_value(self, value, expression, connection):
        """
        Converts a value as returned by the database to a Python object.
        """
        if value is None:
            return value
        # convert string to list of floats
        return list(map(float, value.strip("[]").split(",")))


class EuclideanDistance(Func):
    function = ""
    template = "(%(expressions)s::vector) <-> '%(compare_to)s'"
    output_field = models.FloatField()

    def __init__(self, expression: str, compare_to: List[float], **extra):
        super().__init__(expression, **extra)
        self.extra["compare_to"] = compare_to


class CosineSimilarity(Func):
    function = ""
    template = "(%(expressions)s::vector) <=> '%(compare_to)s'"
    output_field = models.FloatField()

    def __init__(self, expression: str, compare_to: List[float], **extra):
        super().__init__(expression, **extra)
        self.extra["compare_to"] = compare_to


class InnerProduct(Func):
    function = ""
    template = "(%(expressions)s::vector <#> '%(compare_to)s') * -1"
    output_field = models.FloatField()

    def __init__(self, expression: str, compare_to: List[float], **extra):
        super().__init__(expression, **extra)
        self.extra["compare_to"] = compare_to
