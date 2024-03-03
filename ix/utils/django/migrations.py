from django.db import migrations


class UpdateComponentClassPath(migrations.RunPython):
    """Reusable migration operation to migrate a component from one class_path to another.

    This facilitates the deprecation of a component class_path, and the migration of existing
    instances to a new class_path.
    """

    def __init__(self, changes):
        self.changes = changes
        super().__init__(self.update_class_path)

    def update_class_path(self, apps, schema_editor):
        NodeType = apps.get_model("chains", "NodeType")
        ChainNode = apps.get_model("chains", "ChainNode")
        for existing, new in self.changes:
            try:
                old_type = NodeType.objects.get(class_path=existing)
            except NodeType.DoesNotExist:
                old_type = None

            try:
                new_type = NodeType.objects.get(class_path=new)
            except NodeType.DoesNotExist:
                # new node_type doesn't exist in test envs
                return

            # point all nodes at the new type
            ChainNode.objects.filter(class_path=existing).update(
                class_path=new, node_type_id=new_type.id
            )

            if old_type:
                NodeType.objects.filter(class_path=existing).delete()
            print(f"Migrated {existing} to {new}")
