import pytest
import pytest_asyncio
from asgiref.sync import sync_to_async
from pydantic import BaseModel

from ix.skills.runnable import RunSkill
from ix.skills.tests.test_api import afake_skill, MOCK_TEST_FUNC_SCHEMA


@pytest.mark.django_db
class TestRunSkill:
    @pytest_asyncio.fixture()
    async def askill(self):
        yield await afake_skill()

    async def test_initialize_from_db(self, askill):
        run_skill = await sync_to_async(RunSkill.from_db)(askill.id)
        assert run_skill.skill.id == askill.id
        assert run_skill.skill.func_name == "test_func"

        input_type = run_skill.input_schema
        assert issubclass(input_type, BaseModel)
        assert input_type.schema() == MOCK_TEST_FUNC_SCHEMA

    async def test_invoke_skill(self, askill):
        run_skill = await sync_to_async(RunSkill.from_db)(askill.id)
        output = await run_skill.ainvoke(input=dict(a=1, b=2))
        assert output == 3  # Expecting 1 + 2 = 3
