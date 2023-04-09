from celery import shared_task

from ix.agents.process import AgentProcess
from ix.task_log.models import TaskLogMessage


@shared_task
def resume_task_with_feedback(message_id: int):
    """
    Continue agent process after recieving input from a user.
    """
    message = TaskLogMessage.objects.get(pk=message_id)
    process = AgentProcess(task_id=message.task_id)

    user_input = UserInput(message.data)
    process.start(n=user_input.authorized_ticks, input=message.feedback)
