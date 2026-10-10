from django.core.management.base import BaseCommand

from ix.py_code.parser.parse import import_project_from_dir


class Command(BaseCommand):
    help = "Create a new Project from a directory"

    def add_arguments(self, parser):
        parser.add_argument(
            "directory", type=str, help="The directory where the project is located."
        )

    def handle(self, *args, **kwargs):
        directory = kwargs["directory"]
        project = import_project_from_dir(directory)
        self.stdout.write(
            self.style.SUCCESS('Successfully created project "%s"' % project.name)
        )
