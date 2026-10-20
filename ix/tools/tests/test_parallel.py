"""Exercise IX's real agent resolver and tool dispatcher with scripted models."""

import asyncio
import json
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
from langchain.agents import AgentType
from langchain.tools import Tool
from langchain_community.llms.fake import FakeListLLM
from langchain_core.tools import ToolException

from ix.chains.loaders.agents import (
    initialize_agent,
    initialize_self_ask_with_search,
)
from ix.tools.parallel import (
    MCP_URL,
    USER_AGENT,
    ParallelMCP,
    get_parallel_fetch,
    get_parallel_search,
)


PAGE = "IX supports autonomous agents. Source: https://github.com/kreneskyp/ix"


@pytest.fixture
def mcp(monkeypatch):
    requests = []
    state = {"status": 200, "sse": False, "error": False}
    sync_client, async_client = httpx.Client, httpx.AsyncClient

    def respond(request):
        message = json.loads(request.content)
        requests.append((request, message))
        assert str(request.url) == MCP_URL
        assert request.headers["user-agent"] == USER_AGENT
        assert "authorization" not in request.headers
        assert "text/event-stream" in request.headers["accept"]
        if message["method"] == "initialize":
            assert "mcp-session-id" not in request.headers
            return httpx.Response(
                200,
                headers={"Mcp-Session-Id": "transport-session"},
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {"protocolVersion": "2025-03-26"},
                },
            )
        assert request.headers["mcp-session-id"] == "transport-session"
        assert request.headers["mcp-protocol-version"] == "2025-03-26"
        if message["method"] == "notifications/initialized":
            return httpx.Response(202)
        if state.get("exception"):
            raise state["exception"]
        if state["status"] != 200:
            return httpx.Response(state["status"], text="service error")
        if message["method"] == "tools/list":
            result = {"tools": [{"name": "web_search"}, {"name": "web_fetch"}]}
        else:
            result = {
                "content": [{"type": "text", "text": PAGE}],
                "isError": state["error"],
            }
        response = {"jsonrpc": "2.0", "id": message["id"], "result": result}
        if state.get("rpc_error"):
            response = {
                "jsonrpc": "2.0",
                "id": message["id"],
                "error": {"code": -32602, "message": "bad arguments"},
            }
        if state.get("malformed"):
            return httpx.Response(200, text="not JSON")
        if state["sse"]:
            return httpx.Response(
                200,
                headers={"Content-Type": "text/event-stream"},
                text=': keepalive\n\ndata: {"jsonrpc":"2.0","method":"notifications/progress"}\n\nevent: message\ndata: '
                + json.dumps(response)
                + "\n\n",
            )
        return httpx.Response(200, json=response)

    transport = httpx.MockTransport(respond)
    monkeypatch.setattr(
        httpx, "Client", lambda **kw: sync_client(transport=transport, **kw)
    )
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: async_client(transport=transport, **kw)
    )
    return requests, state


def calls(mcp):
    return [
        message["params"] for _, message in mcp[0] if message["method"] == "tools/call"
    ]


class RecordingLLM(FakeListLLM):
    prompts: list = []

    def _call(self, prompt, **kwargs):
        self.prompts.append(prompt)
        return super()._call(prompt, **kwargs)

    async def _acall(self, prompt, **kwargs):
        return self._call(prompt, **kwargs)


def model():
    return RecordingLLM(
        responses=[
            "Yes.\nFollow up: What does IX support?",
            "So the final answer is: IX supports autonomous agents.",
        ]
    )


def test_default_agent_consumes_search(mcp, monkeypatch):
    for key in (
        "PARALLEL_API_KEY",
        "GOOGLE_API_KEY",
        "SERPER_API_KEY",
        "BING_SUBSCRIPTION_KEY",
    ):
        monkeypatch.delenv(key, raising=False)
    llm = model()
    agent = initialize_self_ask_with_search(llm=llm)
    result = agent.invoke({"input": "What does IX support?"})
    assert result["output"] == "IX supports autonomous agents."
    assert PAGE in llm.prompts[1]
    assert calls(mcp)[0]["name"] == "web_search"
    assert calls(mcp)[0]["arguments"]["search_queries"] == ["What does IX support?"]


@pytest.mark.asyncio
async def test_async_default_agent_consumes_search(mcp):
    llm = model()
    agent = initialize_self_ask_with_search(llm=llm)
    result = await agent.ainvoke({"input": "What does IX support?"})
    assert result["output"] == "IX supports autonomous agents."
    assert PAGE in llm.prompts[1]
    assert len(calls(mcp)) == 1


def test_explicit_tool_preserved(mcp):
    tool = Tool(
        name="Intermediate Answer",
        description="Configured search",
        func=lambda q: "Saved provider result",
    )
    llm = model()
    agent = initialize_self_ask_with_search(llm=llm, tools=[tool])
    agent.invoke({"input": "Question"})
    assert "Saved provider result" in llm.prompts[1]
    assert not mcp[0]


def test_explicit_provider_error_does_not_fall_back(mcp):
    def fail(query):
        raise ToolException("Configured provider failed")

    tool = Tool(name="Intermediate Answer", description="Configured search", func=fail)
    agent = initialize_self_ask_with_search(llm=model(), tools=[tool])
    with pytest.raises(ToolException, match="Configured provider failed"):
        agent.invoke({"input": "Question"})
    assert not mcp[0]


def test_disabled_and_empty_tools_remain_disabled(mcp):
    for kwargs in (
        {"tools": []},
        {"default_search": False},
        {"tools": [], "default_search": True},
    ):
        with pytest.raises((ValueError, TypeError)):
            initialize_self_ask_with_search(llm=model(), **kwargs)
    assert not mcp[0]


def test_other_agents_get_no_implicit_search(mcp):
    with pytest.raises(ValueError, match="At least one tool"):
        initialize_agent(AgentType.ZERO_SHOT_REACT_DESCRIPTION, llm=model(), tools=[])
    tool = Tool(name="local", description="Local tool", func=lambda q: "local")
    agent = initialize_agent(
        AgentType.ZERO_SHOT_REACT_DESCRIPTION, llm=model(), tools=[tool]
    )
    assert [t.name for t in agent.tools] == ["local"]
    assert not mcp[0]


@pytest.mark.parametrize("sse", [False, True])
def test_search_fetch_and_discovery(mcp, sse):
    mcp[1]["sse"] = sse
    assert ParallelMCP().request("tools/list", {})["tools"][0]["name"] == "web_search"
    context = SimpleNamespace(chat_id=str(uuid4()), task_id=str(uuid4()))
    assert get_parallel_search(context=context).invoke("IX agents") == PAGE
    assert (
        get_parallel_fetch(context=context).invoke("https://example.com/page?q=a#part")
        == PAGE
    )
    assert calls(mcp)[1]["arguments"]["urls"] == ["https://example.com/page?q=a#part"]
    assert {c["arguments"]["session_id"] for c in calls(mcp)} == {context.chat_id}


@pytest.mark.asyncio
@pytest.mark.parametrize("sse", [False, True])
async def test_async_search_fetch_and_discovery(mcp, sse):
    mcp[1]["sse"] = sse
    assert len((await ParallelMCP().arequest("tools/list", {}))["tools"]) == 2
    context = SimpleNamespace(chat_id=str(uuid4()), task_id=str(uuid4()))
    assert await get_parallel_search(context=context).ainvoke("IX agents") == PAGE
    assert (
        await get_parallel_fetch(context=context).ainvoke("https://example.com") == PAGE
    )
    assert {c["arguments"]["session_id"] for c in calls(mcp)} == {context.chat_id}


@pytest.mark.asyncio
async def test_conversation_lifecycle_through_agent_resolver(mcp):
    a = SimpleNamespace(chat_id=str(uuid4()), task_id=str(uuid4()))
    b = SimpleNamespace(chat_id=str(uuid4()), task_id=str(uuid4()))

    # IX reloads the graph with the chat context on every turn. Shared transports
    # must not create a global conversation identity.
    async def turn(context):
        return await initialize_self_ask_with_search(
            llm=model(), context=context
        ).ainvoke({"input": "Question"})

    await asyncio.gather(turn(a), turn(b))
    await get_parallel_fetch(context=a).ainvoke("https://example.com")
    await turn(a)
    ids = [c["arguments"]["session_id"] for c in calls(mcp)]
    assert ids.count(a.chat_id) == 3
    assert ids.count(b.chat_id) == 1
    assert a.chat_id != b.chat_id
    reset = SimpleNamespace(chat_id=str(uuid4()), task_id=str(uuid4()))
    await turn(reset)
    assert calls(mcp)[-1]["arguments"]["session_id"] == reset.chat_id
    assert reset.chat_id not in ids


@pytest.mark.asyncio
async def test_retry_retains_conversation_identity(mcp):
    context = SimpleNamespace(chat_id=str(uuid4()), task_id=str(uuid4()))
    tool = initialize_self_ask_with_search(llm=model(), context=context).tools[0]
    mcp[1]["status"] = 429
    with pytest.raises(ToolException, match="HTTP 429"):
        await tool.ainvoke("IX agents")
    mcp[1]["status"] = 200
    assert await tool.ainvoke("IX agents") == PAGE
    assert {c["arguments"]["session_id"] for c in calls(mcp)} == {context.chat_id}


def test_standalone_task_and_research_identity(mcp):
    context = SimpleNamespace(chat_id=None, task_id=str(uuid4()))
    get_parallel_search(context=context).invoke("task")
    assert calls(mcp)[0]["arguments"]["session_id"] == context.task_id
    tool = get_parallel_search()
    tool.invoke("one")
    tool.invoke("two")
    get_parallel_search().invoke("new run")
    ids = [c["arguments"]["session_id"] for c in calls(mcp)]
    assert ids[1] == ids[2]
    assert ids[3] != ids[1]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "failure,match",
    [
        ({"status": 503}, "HTTP 503"),
        ({"error": True}, "IX supports"),
        ({"rpc_error": True}, "request failed"),
        ({"malformed": True}, "Could not read"),
        ({"exception": httpx.ReadTimeout("timeout")}, "timed out"),
        ({"exception": httpx.ConnectError("unavailable")}, "Could not read"),
    ],
)
def test_failures_are_visible(mcp, asynchronous, failure, match):
    mcp[1].update(failure)
    tool = initialize_self_ask_with_search(llm=model()).tools[0]
    with pytest.raises(ToolException, match=match):
        if asynchronous:
            asyncio.run(tool.ainvoke("query"))
        else:
            tool.invoke("query")
    assert len(calls(mcp)) == 1


@pytest.mark.asyncio
async def test_async_cancellation_propagates(mcp):
    mcp[1]["exception"] = asyncio.CancelledError()
    with pytest.raises(asyncio.CancelledError):
        await initialize_self_ask_with_search(llm=model()).ainvoke(
            {"input": "Question"}
        )
    assert len(calls(mcp)) == 1


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com",
        "https://",
        "https://user:secret@example.com",
        "",
    ],
)
def test_invalid_urls_do_not_make_requests(mcp, url):
    with pytest.raises((ToolException, ValueError)):
        get_parallel_fetch().invoke(url)
    assert not mcp[0]


def test_timeout_must_be_positive(mcp):
    with pytest.raises(ValueError, match="positive"):
        get_parallel_search(timeout=0)
