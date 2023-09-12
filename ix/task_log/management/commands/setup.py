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
            "ix_v2",
            "code_v2",
            "pirate_v1",
            "wikipedia_v1",
            "klarna_v1",
            "bot_smith_v1",
        ]:
            print(f"Loading fixture: {fixture}")
            call_command("loaddata", fixture)
        print("Done!")
