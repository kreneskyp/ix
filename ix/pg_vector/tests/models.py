from typing import List

from django.db.models import QuerySet

from ix.pg_vector.fields import CosineSimilarity, EuclideanDistance, InnerProduct
from ix.pg_vector.utils import get_embedding


class PGVectorMixin:
    """QuerySet mixin for pg_vector operations."""

    def cosine_similarity(
        self: QuerySet, compare_to: List[float] | str, field_name: str = "embedding"
    ) -> QuerySet:
        """
        Returns a queryset annotated with the cosine similarity between
        the given embedding and the given field.
        """
        if isinstance(compare_to, str):
            compare_to = get_embedding(compare_to)

        return self.annotate(
            similarity=CosineSimilarity(field_name, compare_to)
        ).order_by("-similarity")

    def euclidean_distance(
        self: QuerySet, compare_to: List[float] | str, field_name: str = "embedding"
    ) -> QuerySet:
        """
        Returns a queryset annotated with the euclidean distance between
        the given embedding and the given field.
        """
        if isinstance(compare_to, str):
            compare_to = get_embedding(compare_to)

        return self.annotate(
            distance=EuclideanDistance(field_name, compare_to)
        ).order_by("distance")

    def inner_product(
        self: QuerySet, compare_to: List[float] | str, field_name: str = "embedding"
    ) -> QuerySet:
        """
        Returns a queryset annotated with the inner product between
        the given embedding and the given field.
        """
        if isinstance(compare_to, str):
            compare_to = get_embedding(compare_to)

        return self.annotate(product=InnerProduct(field_name, compare_to)).order_by(
            "-product"
        )
