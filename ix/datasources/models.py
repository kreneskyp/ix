import uuid

from django.db import models

from ix.chains.models import Chain


class DataSource(models.Model):
    """
    Represents a data source that can be imported and used by chains and agents.

    Data sources are defined by a `config` that will generally include an identifier
    (url, path, account, etc), credentials, and other options needed to access the
    data.

    Data sources are imported by a `retrieval_chain` initialized using the `config`.
    Retrieval chains may be any type of Chain or Agent. The retrieval chain will
    generally use a load, splitter, and vectorstore to import the data. Chains
    may be multi-step processes or workflows spanning multiple chains and agents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("ix_users.User", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    # Config stores the config properties for a loader template
    config = models.JSONField()

    # Retrieval chain - chain used to import this datasource
    retrieval_chain = models.ForeignKey(Chain, on_delete=models.SET_NULL, null=True)
