from django.core.management.base import BaseCommand
from ix.agents.process import AgentProcess
from ix.task_log.models import Task


class Command(BaseCommand):
    help = "Prints the list of commands for an agent"

    def add_arguments(self, parser):
        parser.add_argument("-n", type=int, default=1, help="Number of ticks to run")
        parser.add_argument("-t", "--task", type=str, help="Task id to load")

    def handle(self, *args, **options):
        task = Task.objects.all()[0]
        process = AgentProcess(task)
        print(process.command_registry.command_prompt())
