from ix.chains.fixture_src.targets import CHAIN_TARGET
from langchain import (
    GoogleSearchAPIWrapper,
    GoogleSerperAPIWrapper,
    ArxivAPIWrapper,
    WikipediaAPIWrapper,
)
from langchain.utilities import (
    BingSearchAPIWrapper,
    DuckDuckGoSearchAPIWrapper,
    GraphQLAPIWrapper,
    LambdaWrapper,
    PubMedAPIWrapper,
)

from ix.api.chains.types import NodeTypeField
from ix.chains.fixture_src.common import VERBOSE

NAME = {
    "name": "name",
    "type": "str",
    "default": "",
    "style": {"width": "100%"},
}

DESCRIPTION = {
    "name": "description",
    "type": "str",
    "default": "",
    "input_type": "textarea",
    "style": {"width": "100%"},
}

RETURN_DIRECT = {
    "name": "return_direct",
    "type": "boolean",
    "default": False,
}

TOOL_BASE_FIELDS = [RETURN_DIRECT, VERBOSE]

ARXIV_SEARCH = {
    "class_path": "ix.tools.arxiv.get_arxiv",
    "type": "tool",
    "name": " search",
    "description": "Tool that searches Arxiv for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields_from_model(
        ArxivAPIWrapper,
        include=[
            "top_k_results",
            "ARXIV_MAX_QUERY_LENGTH",
            "load_max_docs",
            "load_all_available_meta",
            "doc_content_chars_max",
        ],
    ),
}

BING_SEARCH = {
    "class_path": "ix.tools.bing.get_bing_search",
    "type": "tool",
    "name": "Bing Search",
    "description": "Tool that searches Bing for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields_from_model(
        BingSearchAPIWrapper,
        include=["bing_subscription_key", "bing_search_url", "k"],
        field_options={
            "bing_subscription_key": {
                "input_type": "secret",
            },
            "bing_search_url": {
                "style": {"width": "100%"},
            },
        },
    ),
}

CHAIN_AS_TOOL = {
    "class_path": "ix.chains.tools.chain_as_tool",
    "type": "tool",
    "name": "Chain Tool",
    "description": "Tool that runs a chain. Any chain may be converted into a tool.",
    "connectors": [CHAIN_TARGET],
    "fields": [NAME, DESCRIPTION] + TOOL_BASE_FIELDS,
}

DUCK_DUCK_GO_SEARCH = {
    "class_path": "ix.tools.duckduckgo.get_ddg_search",
    "type": "tool",
    "name": "DuckDuckGo Search",
    "description": "Tool that searches DuckDuckGo for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields_from_model(
        DuckDuckGoSearchAPIWrapper,
        include=["k", "region", "safesearch", "time", "max_results"],
    ),
}

GOOGLE_SEARCH = {
    "class_path": "ix.tools.google.get_google_search",
    "type": "tool",
    "name": "Google Search",
    "description": "Tool that searches Google for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields_from_model(
        GoogleSearchAPIWrapper,
        include=["google_api_key", "google_cse_id", "k", "siterestrict"],
        field_options={
            "google_api_key": {
                "input_type": "secret",
            },
            "google_cse_id": {
                "input_type": "secret",
            },
        },
    ),
}

GOOGLE_SERPER = {
    "class_path": "ix.tools.google.get_google_serper",
    "type": "tool",
    "name": "Google Serper",
    "description": "Tool that searches Google for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields_from_model(
        GoogleSerperAPIWrapper,
        include=["k", "gl", "hl", "type", "tbs", "serper_api_key"],
        field_options={
            "serper_api_key": {
                "input_type": "secret",
            },
        },
    ),
}

GRAPHQL_TOOL = {
    "class_path": "ix.tools.graphql.get_graphql_tool",
    "type": "tool",
    "name": "GraphQL Tool",
    "description": "Tool that searches GraphQL for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields_from_model(
        GraphQLAPIWrapper, include=["graphql_endpoint"]
    ),
}

LAMBDA_API = {
    "class_path": "ix.tools.lambda_api.get_lambda_api",
    "type": "tool",
    "name": "Lambda API",
    "description": "Tool that searches Lambda for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields_from_model(
        LambdaWrapper,
        include=["function_name", "awslambda_tool_name", "awslambda_tool_description"],
    ),
}

PUB_MED = {
    "name": "Pubmed",
    "description": "Pubmed search engine",
    "class_path": "ix.tools.pubmed.get_pubmed",
    "type": "tool",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields_from_model(
        PubMedAPIWrapper,
        include=[
            "max_retry",
            "top_k_results",
            "ARXIV_MAX_QUERY_LENGTH",
            "doc_content_chars_max",
            "email",
        ],
    ),
}

REQUESTS_DELETE = {
    "name": "http_delete",
    "description": "wrapper around python http requests delete method",
    "class_path": "ix.tools.requests.get_tools_requests_delete",
    "type": "tool",
    "fields": TOOL_BASE_FIELDS,
}

REQUESTS_GET = {
    "name": "http_get",
    "description": "wrapper around python http requests get method. Used to"
    "fetch response from a URL",
    "class_path": "ix.tools.requests.get_tools_requests_get",
    "type": "tool",
    "fields": TOOL_BASE_FIELDS,
}

REQUESTS_PATCH = {
    "name": "http_patch",
    "description": "wrapper around python http requests patch method",
    "class_path": "ix.tools.requests.get_tools_requests_patch",
    "type": "tool",
    "fields": TOOL_BASE_FIELDS,
}

REQUESTS_POST = {
    "name": "http_post",
    "description": "wrapper around python http requests post method",
    "class_path": "ix.tools.requests.get_tools_requests_post",
    "type": "tool",
    "fields": TOOL_BASE_FIELDS,
}

REQUESTS_PUT = {
    "name": "http_put",
    "description": "wrapper around python http requests put method",
    "class_path": "ix.tools.requests.get_tools_requests_put",
    "type": "tool",
    "fields": TOOL_BASE_FIELDS,
}

WIKIPEDIA = {
    "name": "Wikipedia",
    "description": "Wikipedia search engine",
    "class_path": "ix.tools.wikipedia.get_wikipedia",
    "type": "tool",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields_from_model(
        WikipediaAPIWrapper,
        include=[
            "top_k_results",
            "lang",
            "load_all_available_meta",
            "doc_content_chars_max",
        ],
    ),
}

WOLFRAM = {
    "name": "Wolfram Alpha",
    "description": "Wolfram Alpha search engine for math and science",
    "class_path": "ix.tools.wolfram_alpha.get_wolfram_alpha",
    "display_type": "node",
    "type": "tool",
    "fields": TOOL_BASE_FIELDS
    + [
        {
            "name": "wolfram_alpha_app_id",
            "label": "Wolfram Alpha App ID",
            "type": "str",
            "input_type": "secret",
        },
    ],
}


TOOLS = [
    ARXIV_SEARCH,
    BING_SEARCH,
    CHAIN_AS_TOOL,
    DUCK_DUCK_GO_SEARCH,
    GOOGLE_SEARCH,
    GOOGLE_SERPER,
    GRAPHQL_TOOL,
    LAMBDA_API,
    PUB_MED,
    REQUESTS_DELETE,
    REQUESTS_GET,
    REQUESTS_PATCH,
    REQUESTS_POST,
    REQUESTS_PUT,
    WIKIPEDIA,
    WOLFRAM,
]
