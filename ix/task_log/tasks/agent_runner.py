from celery_singleton import Singleton
from ix.agents.process import AgentProcess
from ix.server.celery import app


@app.task(
    base=Singleton,
    unique_on=[
        "task_id",
    ],
)
def start_agent_loop(task_id: str):
    """
    Start agent process loop.

    This method uses celery `Singleton`. If executed again with the same `task_id`, it will not start a new process.
    An AsyncResult for the running task will be returned.

    This method expects `task_id` to be a string to be compatible with celery Singleton.
    """
    process = AgentProcess(task_id=task_id)
    return process.start()
