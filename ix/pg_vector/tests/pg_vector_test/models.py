from django.db import models

from ix.pg_vector.fields import VectorField
from ix.pg_vector.utils import get_embedding


class EmbeddingManager(models.Manager):
    """
    Custom manager for the Embedding model.
    """

    def create_with_embedding(self, key, text):
        """
        Creates a new Embedding object with a vector embedding generated
        from the given text using OpenAI's API.
        """
        embedding = get_embedding(text)
        return self.create(key=key, text=text, embedding=embedding)


class Embedding(models.Model):
    """
    Model representing a text and its corresponding vector embedding.
    """

    key = models.CharField(max_length=255, unique=True)
    text = models.TextField()
    embedding = VectorField(size=3)
    null_embedding = VectorField(size=3, null=True)
    indexed_embedding = VectorField(size=3, null=True)

    objects = EmbeddingManager()

    class Meta:
        db_table = "embeddings"

    def __str__(self):
        return self.key
