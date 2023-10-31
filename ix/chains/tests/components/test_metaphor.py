import pytest
from langchain.tools import Tool

from ix.chains.fixture_src.tools import (
    METAPHOR_SEARCH_CLASS_PATH,
    METAPHOR_CONTENTS_CLASS_PATH,
    METAPHOR_FIND_SIMILAR_CLASS_PATH,
)


METAPHOR_SEARCH = {
    "class_path": METAPHOR_SEARCH_CLASS_PATH,
    "config": {
        "metaphor_api_key": "fake_key",
    },
}

METAPHOR_CONTENTS = {
    "class_path": METAPHOR_CONTENTS_CLASS_PATH,
    "config": {
        "metaphor_api_key": "fake_key",
    },
}

METAPHOR_SIMILAR = {
    "class_path": METAPHOR_FIND_SIMILAR_CLASS_PATH,
    "config": {
        "metaphor_api_key": "fake_key",
    },
}


@pytest.mark.django_db
class TestMetaphorTools:
    async def test_load_search(self, aload_chain, mock_config_secrets):
        config = await mock_config_secrets(METAPHOR_SEARCH, ["metaphor_api_key"])
        component = await aload_chain(config)
        assert isinstance(component, Tool)
        assert component.name == "metaphor_search"

    async def test_load_contents(self, aload_chain, mock_config_secrets):
        config = await mock_config_secrets(METAPHOR_CONTENTS, ["metaphor_api_key"])
        component = await aload_chain(config)
        assert isinstance(component, Tool)
        assert component.name == "metaphor_get_contents"

    async def test_load_similar(self, aload_chain, mock_config_secrets):
        config = await mock_config_secrets(METAPHOR_SIMILAR, ["metaphor_api_key"])
        component = await aload_chain(config)
        assert isinstance(component, Tool)
        assert component.name == "metaphor_find_similar"
