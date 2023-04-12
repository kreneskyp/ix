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
        parser.add_argument(
            "-r",
            "--resume",
            action="store_true",
            help="Resume from the lastest user feedback",
        )

    def handle(self, *args, **options):
        # Set options
        n_ticks = options["n"]
        task_id = options["task"]
        resume = options["resume"]
        feedback_message = None

        if resume:
            # Find the latest feedback message for the task
            feedback_message = (
                TaskLogMessage.objects.filter(task_id=task_id, content_type="FEEDBACK")
                .order_by("-created_at")
                .first()
            )

            if feedback_message:
                # Check if the feedback message is the last message for the task
                last_message = (
                    TaskLogMessage.objects.filter(task_id=task_id)
                    .order_by("-created_at")
                    .first()
                )

                if feedback_message != last_message:
                    # Ask the user if they want to remove all later messages or exit
                    print(
                        "The latest feedback message is not the last message for this task."
                    )
                    remove_choice = input(
                        "Do you want to remove all later messages and resume? (Y/n): "
                    )

                    if remove_choice.strip().lower() in {"y", "yes"}:
                        # Remove all later messages
                        TaskLogMessage.objects.filter(
                            task_id=task_id, created_at__gt=feedback_message.created_at
                        ).delete()
                    else:
                        # Exit
                        print("Exiting...")
                        return

        # Start agent process
        process = AgentProcess(task_id=task_id)

        process.start(n=n_ticks, user_input_msg=feedback_message)
