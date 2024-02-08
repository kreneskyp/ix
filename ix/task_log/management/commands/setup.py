from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Initial setup for IX service"""

    def handle(self, *args, **options):
        print("IX setup running...")
        call_command("migrate")
        call_command("import_langchain")
        for fixture in [
            "fake_user",
            "agent/ix",
            "agent/readme",
            "agent/code2",
            "agent/dalle",
            "agent/gemini",
            "agent/owl",
            "agent/pirate",
            "agent/wikipedia",
            "agent/klarna",
            "agent/schemas",
            "agent/skills",
            "agent/smithy",
            "agent/metaphor",
            "agent/ingest_url",
            "agent/ingest",
            "agent/knowledge",
            "agent/vision",
            "ix_api",
        ]:
            print(f"Loading fixture: {fixture}")
            call_command("loaddata", fixture)
        print("Done!")
