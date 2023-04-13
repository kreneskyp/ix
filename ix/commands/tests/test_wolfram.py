import pytest

from ix.commands.wolfram import search_wolfram


class TestSearchWolfram:
    def test_search_wolfram_with_valid_query(self):
        query = "What is the capital of France?"
        results = search_wolfram(query)
        assert len(results) > 0
        assert all(isinstance(result, tuple) for result in results)

    def test_search_wolfram_with_empty_query(self):
        query = ""
        with pytest.raises(ValueError):
            search_wolfram(query)

    def test_search_wolfram_with_missing_app_id(self, monkeypatch):
        monkeypatch.delenv("WOLFRAM_APP_ID", raising=False)
        query = "What is the capital of France?"
        with pytest.raises(ValueError):
            search_wolfram(query)
