import os
import logging
from typing import List
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googlesearch import search

from ix.commands import command

logger = logging.getLogger(__name__)


def google_search_api(query: str) -> List[str]:
    """Searches Google using the Custom Search API."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    cx_id = os.environ.get("GOOGLE_CX_ID")
    if not api_key or not cx_id:
        raise ValueError("GOOGLE_API_KEY or GOOGLE_CX_ID environment variable not set.")
    logger.debug(f"Searching Google API: {query}")
    service = build("customsearch", "v1", developerKey=api_key)

    try:
        res = service.cse().list(
            q=query,
            cx=cx_id,
        ).execute()
        if "items" in res:
            return [item["link"] for item in res["items"]]
    except HttpError as e:
        logger.error(f"Error searching Google API: {e}")
        pass

    return []


def google_search_scrape(query: str) -> List[str]:
    """Searches Google by scraping search results."""
    logger.info("Scraping Google search...")
    return list(search(query, num=10))


@command(name="google_search", description="Search Google")
def google_search(query: str) -> List[str]:
    """Searches Google using either the Custom Search API or search scraping."""
    if "GOOGLE_API_KEY" in os.environ:
        try:
            return google_search_api(query)
        except ValueError as e:
            logger.error(f"Error searching Google: {str(e)}")
            raise ValueError(f"Error searching Google: {str(e)}")
    else:
        try:
            return google_search_scrape(query)
        except Exception as e:
            logger.error(f"Error searching Google: {str(e)}")
            raise ValueError(f"Error searching Google: {str(e)}")
