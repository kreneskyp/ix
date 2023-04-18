import pytest
from ix.commands.google import google_search


class TestGoogleSearch:
    def test_google_search_scrape(self):
        query = "Python"
        results = google_search(query)
        assert len(results) == 10
        assert all("python" in result.lower() for result in results)

    @pytest.mark.skipif("not ('GOOGLE_API_KEY' in os.environ)")
    def test_google_search_api(self):
        query = "Python"
        results = google_search(query)
        assert len(results) > 0
        assert all("python" in result.lower() for result in results)
