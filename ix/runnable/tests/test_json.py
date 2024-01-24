import pytest
from ix.runnable.json import RunJSONTransform, BaseType, JSONPath


@pytest.fixture()
def sample_json_data():
    return {
        "name": "John Doe",
        "age": 30,
        "address": {"street": "123 Main St", "city": "Anytown", "state": "CA"},
        "hobbies": ["reading", "cycling", "traveling"],
    }


@pytest.mark.asyncio
class TestRunJSONTransform:
    async def test_initialization(self):
        # Test initialization of the component
        json_transform = RunJSONTransform(
            base=BaseType.SINGLE, json_path=JSONPath(path="$.name")
        )
        assert json_transform.base == BaseType.SINGLE
        assert json_transform.json_path.path == "$.name"
        assert json_transform.json_path.is_list is False

    async def test_single_mode(self, sample_json_data):
        # Test single mode
        json_transform = RunJSONTransform(
            base=BaseType.SINGLE, json_path=JSONPath(path="$.name")
        )
        result = await json_transform.ainvoke(sample_json_data)
        assert result == "John Doe"

        # Test single mode with is_list=True
        json_transform = RunJSONTransform(
            base=BaseType.SINGLE, json_path=JSONPath(path="$.name", is_list=True)
        )
        result = await json_transform.ainvoke(sample_json_data)
        assert result == ["John Doe"]

    async def test_list_mode(self, sample_json_data):
        # Test list mode
        json_transform = RunJSONTransform(
            base=BaseType.LIST, json_path=[JSONPath(path="$.hobbies[*]")]
        )
        result = await json_transform.ainvoke(sample_json_data)
        assert result == ["reading", "cycling", "traveling"]

        # Test list mode with is_list=True
        json_transform = RunJSONTransform(
            base=BaseType.LIST, json_path=[JSONPath(path="$.hobbies[*]", is_list=True)]
        )
        result = await json_transform.ainvoke(sample_json_data)
        assert result == [["reading", "cycling", "traveling"]]

    async def test_object_mode(self, sample_json_data):
        # Test object mode
        json_transform = RunJSONTransform(
            base=BaseType.OBJECT,
            json_path={
                "name": JSONPath(path="$.name"),
                "city": JSONPath(path="$.address.city"),
            },
        )
        result = await json_transform.ainvoke(sample_json_data)
        assert result == {"name": "John Doe", "city": "Anytown"}

        # Test object mode with is_list=True
        json_transform = RunJSONTransform(
            base=BaseType.OBJECT,
            json_path={
                "name": JSONPath(path="$.name", is_list=True),
                "city": JSONPath(path="$.address.city", is_list=True),
            },
        )
        result = await json_transform.ainvoke(sample_json_data)
        assert result == {"name": ["John Doe"], "city": ["Anytown"]}

    async def test_single_mode_is_list_true(self, sample_json_data):
        # Test single mode with is_list=True and path returns single value
        json_transform = RunJSONTransform(
            base=BaseType.SINGLE, json_path=JSONPath(path="$.name", is_list=True)
        )
        result = await json_transform.ainvoke(sample_json_data)
        assert result == ["John Doe"]

        # Test single mode with is_list=True and path returns no value
        json_transform = RunJSONTransform(
            base=BaseType.SINGLE, json_path=JSONPath(path="$.nonexistent", is_list=True)
        )
        result = await json_transform.ainvoke(sample_json_data)
        assert result == []

    async def test_list_mode_is_list_true(self, sample_json_data):
        # Test list mode with is_list=True and path returns multiple values
        json_transform = RunJSONTransform(
            base=BaseType.LIST, json_path=[JSONPath(path="$.hobbies[*]", is_list=True)]
        )
        result = await json_transform.ainvoke(sample_json_data)
        assert result == [["reading", "cycling", "traveling"]]

        # Test list mode with is_list=True and path returns no value
        json_transform = RunJSONTransform(
            base=BaseType.LIST,
            json_path=[JSONPath(path="$.nonexistent[*]", is_list=True)],
        )
        result = await json_transform.ainvoke(sample_json_data)
        assert result == [[]]

    async def test_object_mode_is_list_true(self, sample_json_data):
        # Test object mode with is_list=True and paths return values
        json_transform = RunJSONTransform(
            base=BaseType.OBJECT,
            json_path={
                "name": JSONPath(path="$.name", is_list=True),
                "city": JSONPath(path="$.address.city", is_list=True),
            },
        )
        result = await json_transform.ainvoke(sample_json_data)
        assert result == {"name": ["John Doe"], "city": ["Anytown"]}

        # Test object mode with is_list=True and one path returns no value
        json_transform = RunJSONTransform(
            base=BaseType.OBJECT,
            json_path={
                "name": JSONPath(path="$.nonexistent", is_list=True),
                "city": JSONPath(path="$.address.city", is_list=True),
            },
        )
        result = await json_transform.ainvoke(sample_json_data)
        assert result == {"name": [], "city": ["Anytown"]}
