import pytest

from ix.pg_vector.fields import (
    CosineSimilarity,
    EuclideanDistance,
    InnerProduct,
)
from ix.pg_vector.tests.pg_vector_test.models import Embedding


class TestVectorField:
    @pytest.fixture
    def embeddings(self, db):
        Embedding.objects.create(
            key="first", text="This is the first test.", embedding=[1.1, 2.1, 3.1]
        )
        Embedding.objects.create(
            key="second", text="This is the second test.", embedding=[4.0, 5.0, 6.0]
        )
        Embedding.objects.create(
            key="third", text="This is the third test.", embedding=[7.0, 8.0, 9.0]
        )

    def test_create_embedding(self, embeddings):
        """Test that row can be created with vector field."""
        first_embedding = Embedding.objects.get(key="first")
        assert first_embedding.text == "This is the first test."
        assert isinstance(first_embedding.embedding, list)
        assert isinstance(first_embedding.embedding[0], float)
        assert first_embedding.embedding == [1.1, 2.1, 3.1]

    def test_cosine_similarity_lookup(self, embeddings):
        # compare first embedding to itself
        first_embedding = Embedding.objects.get(key="first")
        results = Embedding.objects.annotate(
            cosine_distance=CosineSimilarity("embedding", first_embedding.embedding)
        ).order_by("cosine_distance")
        assert results[0].key == "first"

        # test that it can be combined with other lookups
        filtered = results.exclude(key="first")
        assert filtered[0].key == "second"

    def test_euclidean_distance_lookup(self, embeddings):
        # compare first embedding to itself
        first_embedding = Embedding.objects.get(key="first")
        results = Embedding.objects.annotate(
            euclidean_distance=EuclideanDistance("embedding", first_embedding.embedding)
        ).order_by("euclidean_distance")
        assert results[0].key == "first"

        # test that it can be combined with other lookups
        filtered = results.exclude(key="first")
        assert filtered[0].key == "second"

    def test_negative_inner_product_lookup(self, embeddings):
        # compare first embedding to itself
        first_embedding = Embedding.objects.get(key="first")
        results = Embedding.objects.annotate(
            negative_inner_product=InnerProduct("embedding", first_embedding.embedding)
        ).order_by("negative_inner_product")
        assert results[0].key == "first"

        # test that it can be combined with other lookups
        filtered = results.exclude(key="first")
        assert filtered[0].key == "second"

    @pytest.mark.skip()
    def test_create_with_embedding(self, embeddings):
        Embedding.objects.create_with_embedding(
            key="fourth", text="This is the fourth test."
        )
        fourth_embedding = Embedding.objects.get(key="fourth")
        assert fourth_embedding.text == "This is the fourth test."
        assert len(fourth_embedding.embedding) == 512
