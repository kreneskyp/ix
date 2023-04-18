from typing import List, Tuple
import os
import wolframalpha

from ix.commands import command


@command(name="search_wolfram", description="Search Wolfram.")
def search_wolfram(search_string: str) -> List[Tuple[str, str]]:
    """Searches Wolfram for the given search string and returns a list of (title, plaintext) tuples."""
    app_id = os.environ.get("WOLFRAM_APP_ID")
    if not app_id:
        raise ValueError("WOLFRAM_APP_ID environment variable not set.")
    if not search_string:
        raise ValueError("search_string is required")
    client = wolframalpha.Client(app_id)
    res = client.query(search_string)
    results = []
    for pod in res.pods:
        for subpod in pod.subpods:
            results.append((pod.title, subpod.plaintext))
    return results
