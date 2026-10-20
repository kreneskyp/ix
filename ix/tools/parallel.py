"""Keyless Parallel Search MCP tools using Streamable HTTP."""

import json
from typing import Any, Optional
from urllib.parse import urlsplit
from uuid import uuid4

import httpx
from langchain.tools import Tool
from langchain_core.tools import ToolException


MCP_URL = "https://search.parallel.ai/mcp"
USER_AGENT = "agent-ix/0.2.0 (+https://github.com/kreneskyp/ix)"
PROTOCOL_VERSION = "2025-03-26"


class ParallelMCP:
    """A small HTTP MCP client. Connection state is local to each operation.

    Conversation identity is passed in tool arguments, independently of HTTP
    sessions, so simultaneous chats never overwrite each other's identity.
    """

    def __init__(self, timeout: float = 30):
        if timeout <= 0:
            raise ValueError("Parallel timeout must be positive")
        self.timeout = timeout

    @staticmethod
    def _headers() -> dict:
        return {
            "Accept": "application/json, text/event-stream",
            "User-Agent": USER_AGENT,
        }

    @staticmethod
    def _requests(method: str, params: dict):
        yield {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "agent-ix", "version": "0.2.0"},
            },
        }
        yield {"jsonrpc": "2.0", "method": "notifications/initialized"}
        yield {"jsonrpc": "2.0", "id": 2, "method": method, "params": params}

    @staticmethod
    def _result(message: dict, request_id: int) -> Optional[dict]:
        if message.get("id") != request_id:
            return None
        if "error" in message:
            raise ToolException("Parallel MCP request failed")
        result = message.get("result")
        if not isinstance(result, dict):
            raise ToolException("Parallel MCP returned an invalid result")
        return result

    @classmethod
    def _read(cls, response: httpx.Response, request_id: int) -> dict:
        if "text/event-stream" not in response.headers.get("content-type", ""):
            response.read()
            result = cls._result(response.json(), request_id)
            if result is not None:
                return result
        else:
            data = []
            for line in response.iter_lines():
                if line.startswith("data:"):
                    data.append(line[5:].lstrip(" "))
                elif not line and data:
                    result = cls._result(json.loads("\n".join(data)), request_id)
                    if result is not None:
                        return result
                    data = []
        raise ToolException(
            "Parallel MCP response did not contain the requested result"
        )

    @classmethod
    async def _aread(cls, response: httpx.Response, request_id: int) -> dict:
        if "text/event-stream" not in response.headers.get("content-type", ""):
            await response.aread()
            result = cls._result(response.json(), request_id)
            if result is not None:
                return result
        else:
            data = []
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data.append(line[5:].lstrip(" "))
                elif not line and data:
                    result = cls._result(json.loads("\n".join(data)), request_id)
                    if result is not None:
                        return result
                    data = []
        raise ToolException(
            "Parallel MCP response did not contain the requested result"
        )

    @staticmethod
    def _initialized(headers: dict, response: httpx.Response, result: dict):
        version = result.get("protocolVersion")
        if version not in {"2024-11-05", "2025-03-26", "2025-06-18"}:
            raise ToolException(
                "Parallel MCP negotiated an unsupported protocol version"
            )
        headers["MCP-Protocol-Version"] = version
        if session := response.headers.get("mcp-session-id"):
            headers["Mcp-Session-Id"] = session

    def request(self, method: str, params: dict) -> dict:
        headers = self._headers()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                for message in self._requests(method, params):
                    with client.stream(
                        "POST", MCP_URL, headers=headers, json=message
                    ) as response:
                        response.raise_for_status()
                        if "id" not in message:
                            continue
                        result = self._read(response, message["id"])
                        if message["method"] == "initialize":
                            self._initialized(headers, response, result)
                return result
        except httpx.TimeoutException as exc:
            raise ToolException("Parallel MCP request timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise ToolException(
                f"Parallel MCP returned HTTP {exc.response.status_code}"
            ) from exc
        except (httpx.RequestError, ValueError, TypeError, AttributeError) as exc:
            raise ToolException("Could not read the Parallel MCP response") from exc

    async def arequest(self, method: str, params: dict) -> dict:
        headers = self._headers()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for message in self._requests(method, params):
                    async with client.stream(
                        "POST", MCP_URL, headers=headers, json=message
                    ) as response:
                        response.raise_for_status()
                        if "id" not in message:
                            continue
                        result = await self._aread(response, message["id"])
                        if message["method"] == "initialize":
                            self._initialized(headers, response, result)
                return result
        except httpx.TimeoutException as exc:
            raise ToolException("Parallel MCP request timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise ToolException(
                f"Parallel MCP returned HTTP {exc.response.status_code}"
            ) from exc
        except (httpx.RequestError, ValueError, TypeError, AttributeError) as exc:
            raise ToolException("Could not read the Parallel MCP response") from exc


def _text(result: dict) -> str:
    content = result.get("content", [])
    if not isinstance(content, list):
        raise ToolException("Parallel MCP returned invalid text content")
    text = "\n".join(
        item["text"]
        for item in content
        if isinstance(item, dict)
        and item.get("type") == "text"
        and isinstance(item.get("text"), str)
    )
    if result.get("isError"):
        raise ToolException(text or "Parallel MCP tool failed")
    if not text:
        raise ToolException("Parallel MCP returned no text content")
    return text


def _get_tool(method: str, context: Any, timeout: float, **kwargs: Any) -> Tool:
    # IX loads a graph for each conversation/task. Use its existing opaque UUID,
    # never user text or a connection ID. Standalone tools own one research run.
    session_id = (
        (context.chat_id or context.task_id) if context is not None else str(uuid4())
    )
    client = ParallelMCP(timeout)

    def params(value: str) -> dict:
        if not value.strip():
            raise ToolException("A search query or page URL is required")
        if method == "web_search":
            arguments = {"objective": value, "search_queries": [value]}
        else:
            url = urlsplit(value)
            if (
                url.scheme not in {"http", "https"}
                or not url.hostname
                or url.username
                or url.password
            ):
                raise ToolException("Parallel fetch requires an HTTP or HTTPS URL")
            arguments = {"urls": [value]}
        arguments["session_id"] = session_id
        return {"name": method, "arguments": arguments}

    def run(value: str) -> str:
        return _text(client.request("tools/call", params(value)))

    async def arun(value: str) -> str:
        return _text(await client.arequest("tools/call", params(value)))

    name = "parallel_search" if method == "web_search" else "parallel_fetch"
    description = (
        "Search the web for current information. Input is a search query. Returns excerpts and source URLs."
        if method == "web_search"
        else "Read a web page. Input is one HTTP or HTTPS URL. Returns page text with its source URL."
    )
    return Tool(name=name, description=description, func=run, coroutine=arun, **kwargs)


def get_parallel_search(
    context: Any = None, timeout: float = 30, **kwargs: Any
) -> Tool:
    return _get_tool("web_search", context, timeout, **kwargs)


def get_parallel_fetch(context: Any = None, timeout: float = 30, **kwargs: Any) -> Tool:
    return _get_tool("web_fetch", context, timeout, **kwargs)
