from django.core.management.base import BaseCommand
from django.core.management import call_command
import argparse

from ix.agents.process import AgentProcess
from ix.task_log.models import TaskLogMessage


class Command(BaseCommand):
    help = "Runs agent process with given task id and options"

    def add_arguments(self, parser):
        parser.add_argument("-n", type=int, default=1, help="Number of ticks to run")
        parser.add_argument("-t", "--task", type=int, help="Task id to load")

    def handle(self, *args, **options):
        # Set options
        n_ticks = options["n"]
        task_id = options["task"]

        # Start agent process
        process = AgentProcess(task_id=task_id)
        process.start(n=n_ticks)
