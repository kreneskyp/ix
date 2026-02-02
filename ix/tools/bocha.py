from typing import Dict, List, Optional
import requests
from langchain_core.pydantic_v1 import BaseModel, Extra, Field, root_validator
from langchain_core.utils import get_from_dict_or_env

from ix.chains.asyncio import SyncToAsyncRun
# from ix.chains.loaders.tools import extract_tool_kwargs

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

class BoChaSearchAPIWrapper(BaseModel):
    """Wrapper for BoCha Search API."""

    bocha_api_key: str
    k: int = 10
    search_kwargs: dict = Field(default_factory=dict)
    """Additional keyword arguments to pass to the search request."""

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    def _bocha_search_results(self, search_term: str, count: int) -> List[dict]:

        url = 'https://api.bochaai.com/v1/web-search'
        headers = {
            'Authorization': f'Bearer {self.bocha_api_key}',  # 请替换为你的API密钥
            'Content-Type': 'application/json'
        }
        data = {
            "query": search_term,
            "freshness": "noLimit",  # 搜索的时间范围，
            "summary": True,  # 是否返回长文本摘要
            "count": count
        }

        response = requests.post(url, headers=headers, json=data)
        json_response = response.json()
        print(json_response["data"]["webPages"]["value"])
        return json_response["data"]["webPages"]["value"]

    @root_validator(pre=True)
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key exists in environment."""
        bocha_api_key = get_from_dict_or_env(
            values, "bocha_api_key", "BOCHA_API_KEY"
        )
        values["bocha_api_key"] = bocha_api_key

        return values

    def run(self, query: str) -> str:
        """Run query through BoChaSearch and parse result."""
        snippets = []
        results = self._bocha_search_results(query, count=self.k)
        if len(results) == 0:
            return "No good BoCha Search Result was found"
        for result in results:
            snippets.append(result["snippet"])

        return " ".join(snippets)

    def results(self, query: str, num_results: int) -> List[Dict]:
        """Run query through BoChaSearch and return metadata.

        Args:
            query: The query to search for.
            num_results: The number of results to return.

        Returns:
            A list of dictionaries with the following keys:
                snippet - The description of the result.
                title - The title of the result.
                link - The link to the result.
        """
        metadata_results = []
        results = self._bocha_search_results(query, count=num_results)
        if len(results) == 0:
            return [{"Result": "No good BoCha Search Result was found"}]
        for result in results:
            metadata_result = {
                "snippet": result["snippet"],
                "title": result["name"],
                "link": result["url"],
            }
            metadata_results.append(metadata_result)

        return metadata_results

class BoChaSearchRun(BaseTool):
    """Tool that queries the BoCha search API."""

    name: str = "bocha_search"
    description: str = (
        "A wrapper around BoCha Search. "
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query."
    )
    api_wrapper: BoChaSearchAPIWrapper

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        return self.api_wrapper.run(query)

class AsyncBoChaSearchRun(SyncToAsyncRun, BoChaSearchRun):
    pass


def get_bocha_search(**kwargs) -> BaseTool:
    from ix.chains.loaders.tools import extract_tool_kwargs
    tool_kwargs = extract_tool_kwargs(kwargs)
    wrapper = BoChaSearchAPIWrapper(**kwargs)
    return AsyncBoChaSearchRun(api_wrapper=wrapper, **tool_kwargs)