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
            ChainNode.objects.filter(class_path=existing).update(class_path=new)

            if NodeType.objects.filter(class_path=existing).exists():
                NodeType.objects.filter(class_path=existing).delete()
                print(f"Deleted {existing} from NodeType")
            else:
                NodeType.objects.filter(class_path=existing).update(class_path=new)
            print(f"Migrated {existing} to {new}")

