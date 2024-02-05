LIST_PATH = "/chains/"
DETAIL_PATH = "/chains/{chain_id}"
SERVER = "http://test"

SCHEMA = {
    "openapi": "3.1.0",
    "info": {
        "title": "IX agent editor API",
        "description": "API for editing Agents, Chains, and node_type components",
        "version": "0.1.0",
    },
    "paths": {
        "/chains/": {
            "get": {
                "tags": ["Chains"],
                "summary": "Get Chains",
                "operationId": "get_chains_chains__get",
                "parameters": [
                    {
                        "name": "search",
                        "in": "query",
                        "required": False,
                        "schema": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "title": "Search",
                        },
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "default": 10, "title": "Limit"},
                    },
                    {
                        "name": "offset",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "default": 0, "title": "Offset"},
                    },
                    {
                        "name": "is_agent",
                        "in": "query",
                        "required": False,
                        "schema": {
                            "anyOf": [{"type": "boolean"}, {"type": "null"}],
                            "title": "Is Agent",
                        },
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ChainQueryPage"
                                }
                            }
                        },
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                },
            },
            "post": {
                "tags": ["Chains"],
                "summary": "Create Chain",
                "operationId": "create_chain_chains__post",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CreateChain"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Chain"}
                            }
                        },
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                },
            },
        },
        "/chains/{chain_id}": {
            "get": {
                "tags": ["Chains"],
                "summary": "Get Chain Detail",
                "operationId": "get_chain_detail_chains__chain_id__get",
                "parameters": [
                    {
                        "name": "chain_id",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "title": "Chain Id",
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Chain"}
                            }
                        },
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                },
            },
            "put": {
                "tags": ["Chains"],
                "summary": "Update Chain",
                "operationId": "update_chain_chains__chain_id__put",
                "parameters": [
                    {
                        "name": "chain_id",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "title": "Chain Id",
                        },
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/UpdateChain"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Chain"}
                            }
                        },
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                },
            },
            "delete": {
                "tags": ["Chains"],
                "summary": "Delete Chain",
                "operationId": "delete_chain_chains__chain_id__delete",
                "parameters": [
                    {
                        "name": "chain_id",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "title": "Chain Id",
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/DeletedItem"}
                            }
                        },
                    },
                    "422": {
                        "description": "Validation Error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HTTPValidationError"
                                }
                            }
                        },
                    },
                },
            },
        },
    },
    "components": {
        "schemas": {
            "Chain": {
                "properties": {
                    "id": {
                        "anyOf": [
                            {"type": "string", "format": "uuid"},
                            {"type": "null"},
                        ],
                        "title": "Id",
                    },
                    "name": {"type": "string", "title": "Name"},
                    "description": {"type": "string", "title": "Description"},
                    "created_at": {
                        "anyOf": [
                            {"type": "string", "format": "date-time"},
                            {"type": "null"},
                        ],
                        "title": "Created At",
                    },
                    "is_agent": {
                        "type": "boolean",
                        "title": "Is Agent",
                        "default": True,
                    },
                    "alias": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "title": "Alias",
                    },
                },
                "type": "object",
                "required": ["id", "name", "description", "created_at"],
                "title": "Chain",
            },
            "ChainQueryPage": {
                "properties": {
                    "page_number": {"type": "integer", "title": "Page Number"},
                    "pages": {"type": "integer", "title": "Pages"},
                    "count": {"type": "integer", "title": "Count"},
                    "has_next": {"type": "boolean", "title": "Has Next"},
                    "has_previous": {"type": "boolean", "title": "Has Previous"},
                    "objects": {
                        "items": {"$ref": "#/components/schemas/Chain"},
                        "type": "array",
                        "title": "Objects",
                    },
                },
                "type": "object",
                "required": [
                    "page_number",
                    "pages",
                    "count",
                    "has_next",
                    "has_previous",
                    "objects",
                ],
                "title": "ChainQueryPage",
            },
            "CreateChain": {
                "properties": {
                    "name": {"type": "string", "title": "Name"},
                    "description": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "title": "Description",
                    },
                    "is_agent": {
                        "type": "boolean",
                        "title": "Is Agent",
                        "default": False,
                    },
                    "alias": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "title": "Alias",
                    },
                },
                "type": "object",
                "required": ["name", "description"],
                "title": "CreateChain",
            },
            "HTTPValidationError": {
                "properties": {
                    "detail": {
                        "items": {"$ref": "#/components/schemas/ValidationError"},
                        "type": "array",
                        "title": "Detail",
                    }
                },
                "type": "object",
                "title": "HTTPValidationError",
            },
            "UpdateChain": {
                "properties": {
                    "name": {"type": "string", "title": "Name"},
                    "description": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "title": "Description",
                    },
                    "is_agent": {
                        "type": "boolean",
                        "title": "Is Agent",
                        "default": False,
                    },
                    "alias": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "title": "Alias",
                    },
                },
                "type": "object",
                "required": ["name", "description"],
                "title": "UpdateChain",
            },
            "UpdateEdge": {
                "properties": {
                    "source_id": {
                        "type": "string",
                        "format": "uuid",
                        "title": "Source Id",
                    },
                    "target_id": {
                        "type": "string",
                        "format": "uuid",
                        "title": "Target Id",
                    },
                },
                "type": "object",
                "required": ["source_id", "target_id"],
                "title": "UpdateEdge",
            },
            "ValidationError": {
                "properties": {
                    "loc": {
                        "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
                        "type": "array",
                        "title": "Location",
                    },
                    "msg": {"type": "string", "title": "Message"},
                    "type": {"type": "string", "title": "Error Type"},
                },
                "type": "object",
                "required": ["loc", "msg", "type"],
                "title": "ValidationError",
            },
        }
    },
    "servers": [
        {"url": "http://172.17.0.1:8000/api", "description": "Development server"}
    ],
}

GET_LIST_SCHEMA = {
    "definitions": {
        "Query": {
            "properties": {
                "is_agent": {
                    "anyOf": [{"type": "boolean"}, {"type": "null"}],
                    "title": "Is Agent",
                },
                "limit": {"default": 10, "title": "Limit", "type": "integer"},
                "offset": {"default": 0, "title": "Offset", "type": "integer"},
                "search": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "title": "Search",
                },
            },
            "required": [],
            "type": "object",
        }
    },
    "properties": {"query": {"$ref": "#/definitions/Query"}},
    "required": [],
    "type": "object",
}

POST_LIST_SCHEMA = {
    "definitions": {
        "CreateChain": {
            "properties": {
                "alias": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "title": "Alias",
                },
                "description": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "title": "Description",
                },
                "is_agent": {
                    "default": False,
                    "title": "Is " "Agent",
                    "type": "boolean",
                },
                "name": {"title": "Name", "type": "string"},
            },
            "required": ["name", "description"],
            "title": "CreateChain",
            "type": "object",
        }
    },
    "properties": {"body": {"$ref": "#/definitions/CreateChain"}},
    "required": ["body"],
    "type": "object",
}


GET_DETAIL_SCHEMA = {
    "definitions": {
        "Path": {
            "properties": {
                "chain_id": {"format": "uuid", "title": "Chain Id", "type": "string"}
            },
            "required": ["chain_id"],
            "type": "object",
        }
    },
    "properties": {"path": {"$ref": "#/definitions/Path"}},
    "required": ["path"],
    "type": "object",
}
