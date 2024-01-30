from textwrap import dedent
from uuid import uuid4

from ix.skills.models import Skill
from ix.server.fast_api import app
import pytest
from httpx import AsyncClient

from ix.utils.pydantic import model_from_signature


def mock_test_func(a: int, b: int) -> int:
    """This is a mock test function."""
    return a + b


def mock_test_func_too(a: int, b: str) -> int:
    """This is a mock test function."""
    return 0


MOCK_TEST_FUNC_SCHEMA = model_from_signature("FuncArgs", mock_test_func).schema()
MOCK_TEST_FUNC_TOO_SCHEMA = model_from_signature(
    "FuncArgs", mock_test_func_too
).schema()


async def afake_skill(**kwargs) -> Skill:
    # defaults or override from kwargs
    data = {
        "name": "Test Skill",
        "description": "A test skill",
        "code": dedent(
            '''
        def test_func(a: int, b: int) -> int:
            """This is a mock test function."""
            return a + b
        '''
        ),
        "func_name": "test_func",
        "input_schema": MOCK_TEST_FUNC_SCHEMA,
        "tags": ["test"],
    }
    data.update(kwargs)

    return await Skill.objects.acreate(**data)


@pytest.mark.django_db
class TestSkill:
    async def test_create_skill(self, auser):
        data = {
            "name": "Test Skill",
            "description": "A test skill",
            "code": "def test_func(): pass",
            "tags": ["test"],
            "func_name": "test_func",
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/skills/", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we created the skill
        assert result["name"] == "Test Skill"
        assert result["description"] == "A test skill"
        assert "func_name" in result
        assert result["func_name"] == "test_func"

    async def test_create_skill_with_code_parsing(self, auser):
        # Define a Python function with a docstring and type hints
        code = dedent(
            '''
        def example_function(a: int, b: int) -> int:
            """This is an example function!"""
            return 1
        '''
        )

        data = {
            "name": "Parsed Skill",
            "code": code,
            "tags": ["example"],
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/skills/", json=data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that the API parsed func_name, input_schema, and description correctly
        assert result["func_name"] == "example_function"
        assert result["description"] == "This is an example function!"
        assert result["input_schema"] == MOCK_TEST_FUNC_SCHEMA

    async def test_get_skill(self, auser):
        skill = await afake_skill()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/skills/{skill.id}")

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we got the correct skill detail
        assert result["id"] == str(skill.id)
        assert result["name"] == "Test Skill"

    async def test_update_skill(self, auser):
        skill = await afake_skill()
        assert skill.input_schema != MOCK_TEST_FUNC_TOO_SCHEMA

        update_data = {
            "name": "Updated Skill",
            "code": dedent(
                '''
            def test_func_too(a: int, b: str) -> int:
                """This is an updated mock test function!"""
                return 0
            '''
            ),
            "tags": ["updated"],
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/skills/{skill.id}", json=update_data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we updated the skill
        assert result["name"] == "Updated Skill"
        assert result["tags"] == ["updated"]
        assert result["func_name"] == "test_func_too"
        assert result["input_schema"] == MOCK_TEST_FUNC_TOO_SCHEMA
        assert result["description"] == "This is an updated mock test function!"

    async def test_update_skill_extra_fields(self, auser):
        """
        UX isn't currently allowing these fields to be set directly but
        the API does allow it.
        """
        skill = await afake_skill()
        assert skill.input_schema != MOCK_TEST_FUNC_TOO_SCHEMA

        update_data = {
            "name": "Updated Skill",
            "code": dedent(
                '''
            def test_func_too(a: int, b: str) -> int:
                """This is an updated mock test function!"""
                return 0
            '''
            ),
            "description": "overridden description",
            "func_name": "test_func_too",
            "input_schema": {},
            "tags": ["updated"],
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.put(f"/skills/{skill.id}", json=update_data)

        assert response.status_code == 200, response.content
        result = response.json()

        # Check that we updated the skill
        assert result["name"] == "Updated Skill"
        assert result["tags"] == ["updated"]
        assert result["func_name"] == "test_func_too"
        assert result["description"] == "overridden description"
        assert result["input_schema"] == MOCK_TEST_FUNC_TOO_SCHEMA

    async def test_delete_skill(self, auser):
        skill = await afake_skill()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(f"/skills/{skill.id}")

        assert response.status_code == 200, response.content
        result = response.json()
        assert result["id"] == str(skill.id)

        # Ensure the skill is deleted
        assert not await Skill.objects.filter(id=skill.id).aexists()

    async def test_skill_not_found(self, auser):
        non_existent_skill_id = uuid4()

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/skills/{non_existent_skill_id}")

        assert response.status_code == 404
        result = response.json()
        assert result["detail"] == "Skill not found"

    async def test_list_skills(self, auser):
        # Create a few skills for the test
        await afake_skill(name="Skill 1", description="Skill 1 Description")
        await afake_skill(name="Skill 2", description="Skill 2 Description")

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/skills/")

        assert response.status_code == 200, response.content
        results = response.json()

        # Check that we got a list of skills
        objects = results["objects"]
        assert isinstance(objects, list)
        assert len(objects) >= 2
        assert any(skill["name"] == "Skill 1" for skill in objects)
        assert any(skill["name"] == "Skill 2" for skill in objects)
