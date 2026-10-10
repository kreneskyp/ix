from django.core.management.base import BaseCommand

from ix.py_code.models import Project
from ix.py_code.parser.parse import parse_project


class Command(BaseCommand):
    help = "Parse a Project"

    def add_arguments(self, parser):
        parser.add_argument(
            "project_name", type=str, help="The name of the project to parse."
        )

    def handle(self, *args, **kwargs):
        project_name = kwargs["project_name"]
        project = Project.objects.get(name=project_name)
        parse_project(project)
        self.stdout.write(
            self.style.SUCCESS('Successfully parsed project "%s"' % project.name)
        )
