import json
import pytest
from django.core.management import call_command

from ix.chains.models import NodeType


@pytest.mark.django_db
def test_imported_components(snapshot):
    """
    This test double checks any changes to imported component definitions to catch
    mistakes in the import process. I.e. this catches changes that may be bugs but
    don't raise exceptions.

    This means if you change a component or change the import process you will
    need to update the snapshot.

    Note that a failing snapshot doesn't mean there is a bug, it just means you
    need to update the snapshot.
    """
    NodeType.objects.all().delete()
    call_command("import_langchain")

    # Ensure you generate a unique name for each snapshot to avoid overwriting
    snapshot.snapshot_dir = "/var/app/test_data/snapshots/components/"

    nodes = list(NodeType.objects.all().order_by("class_path"))
    for node in nodes:
        # Create a dictionary containing only the fields you want to snapshot
        node_dict = {
            "name": node.name,
            "description": node.description,
            "class_path": node.class_path,
            "type": node.type,
            "display_type": node.display_type,
            "connectors": node.connectors,
            "fields": node.fields,
            "child_field": node.child_field,
            "config_schema": node.config_schema,
        }
        as_json = json.dumps(node_dict, indent=4, sort_keys=True)
        snapshot.assert_match(as_json, snapshot_name=f"{node.class_path}.json")
