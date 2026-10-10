import logging
from typing import Dict, Any, List


from langchain.chains.base import Chain


from ix.agents.models import Agent
from ix.task_log.models import Task
from ix.task_log.tasks.agent_runner import start_agent_loop

logger = logging.getLogger(__name__)


class AsyncChain(Chain):
    """
    Chain that calls another chain asynchronously via celery. The new agent
    will run in a subtask of the parent agent's task.
    """

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        chain_name = inputs["chain_name"]
        task = self.callback_manager.task
        subtask = Task.objects.create(
            parent=task,
            name="subtask: ",
            agent=task.agent,
            autonomous=task.autonomous,
        )
        start_agent_loop.delay(task_id=subtask.id, message_id=None)


class AsyncDelegateChain(Chain):
    """
    Chain that calls another agent asynchronously via celery. The new agent
    will run in a subtask of the parent agent's task.
    """

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        agent_id = inputs["agent_id"]
        agent = Agent.objects.get(id=agent_id)
        task = self.callback_manager.task
        message = self.callback_manager.message
        subtask = Task.objects.create(
            parent=task,
            name="subtask: ",
            agent_id=agent_id,
            chain_id=agent.chain_id,
            autonomous=task.autonomous,
        )

        start_agent_loop.delay(
            task_id=subtask.id, chain_id=agent.chain_id, inputs=inputs
        )
