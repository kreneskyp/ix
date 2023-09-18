from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Initial setup for IX service"""

    def handle(self, *args, **options):
        print("IX setup running...")
        call_command("migrate")
        for fixture in [
            "fake_user",
            "node_types",
            "agent/ix",
            "agent/readme",
            "agent/code",
            "agent/pirate",
            "agent/wikipedia",
            "agent/klarna",
            "agent/smithy",
            "agent/metaphor",
        ]:
            print(f"Loading fixture: {fixture}")
            call_command("loaddata", fixture)
        print("Done!")
