from ix.utils.openapi import get_input_schema
from ix.utils.tests.mock_schema import (
    SCHEMA,
    DETAIL_PATH,
    LIST_PATH,
    GET_DETAIL_SCHEMA,
    GET_LIST_SCHEMA,
    POST_LIST_SCHEMA,
)


class TestGetInputSchema:
    """
    Test using get_input_schema to extract the input schema from an OpenAPI schema.
    """

    def test_path_args(self):
        input_schema = get_input_schema(SCHEMA, DETAIL_PATH, "get")
        assert input_schema == GET_DETAIL_SCHEMA

    def test_query_args(self):
        input_schema = get_input_schema(SCHEMA, LIST_PATH, "get")
        assert input_schema == GET_LIST_SCHEMA

    def test_body_args(self):
        input_schema = get_input_schema(SCHEMA, LIST_PATH, "post")
        assert input_schema == POST_LIST_SCHEMA
