import uuid

import pytest
from django.core.management import call_command

from ix.agents.callback_manager import IxCallbackManager
from ix.chains.models import Chain
from ix.task_log.models import Plan, Artifact
from ix.task_log.tests.fake import fake_task


@pytest.mark.skip()
@pytest.mark.django_db
class TestPlannerV1:
    def test_create_planner_v1(self):
        call_command("create_planner_v1")
        chain = Chain.objects.get()

        task = fake_task()
        callback_manager = IxCallbackManager(task)
        chain_runner = chain.load_chain(callback_manager)
        artifact_id = chain_runner.run(user_input="create a django app for cat memes")

        assert uuid.UUID(artifact_id)
        artifact = Artifact.objects.get(pk=artifact_id)
        assert Plan.objects.filter(pk=artifact.storage["plan_id"]).exists()
