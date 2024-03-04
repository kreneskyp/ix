from typing import Optional

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.utils import Input, Output

from ix.chains.tests.fake import (
    afake_node_sequence,
    afake_runnable,
    afake_node_state_machine,
    afake_chain_edge,
    afake_graph_end,
    BranchMeta,
)
from ix.task_log.tests.fake import afake_chain
import pytest_asyncio

from ix.chains.loaders.core import (
    StateMachinePlaceholder,
    aload_chain_flow,
    ainit_chain_flow,
    ImplicitJoin,
)


@pytest_asyncio.fixture
async def lcel_graph(anode_types) -> dict:
    """Fixture for a LangChain statemachine graph"""
    chain = await afake_chain()
    node1 = await afake_runnable(chain=chain, name="node1", root=False)
    node2 = await afake_runnable(chain=chain, name="node2", root=False)
    graph = await afake_node_state_machine(
        chain=chain,
        root=True,
        branches=[
            (BranchMeta(name="a", description="the first branch"), node1),
            (BranchMeta(name="b", description="the second branch"), node2),
        ],
    )

    assert await chain.nodes.filter(root=True).acount() == 1
    return {
        "chain": chain,
        "graph": graph,
        "node1": node1,
        "node2": node2,
    }


@pytest_asyncio.fixture
async def lcel_graph_with_end(anode_types, lcel_graph) -> dict:
    """A LangGraph graph where one branch connects to an END node"""
    end = await afake_graph_end(chain=lcel_graph["chain"])
    await afake_chain_edge(
        chain=lcel_graph["chain"],
        source=lcel_graph["node1"],
        target=end,
        relation="GRAPH",
        source_key="out",
        target_key="in",
    )
    lcel_graph["graph"].ends = ["a"]
    return lcel_graph


@pytest_asyncio.fixture
async def lcel_graph_with_shared_end(anode_types, lcel_graph) -> dict:
    """A LangGraph graph where multiple branches connect to the same END node"""
    end = await afake_graph_end(chain=lcel_graph["chain"])
    for node in [lcel_graph["node1"], lcel_graph["node2"]]:
        await afake_chain_edge(
            chain=lcel_graph["chain"],
            source=node,
            target=end,
            relation="GRAPH",
            source_key="out",
            target_key="in",
        )
    lcel_graph["graph"].ends = ["a", "b"]
    return lcel_graph


@pytest_asyncio.fixture
async def lcel_graph_with_nested_end(anode_types, lcel_graph) -> dict:
    pass


@pytest_asyncio.fixture
async def lcel_sequence_in_graph(anode_types, lcel_sequence) -> dict:
    """Fixture for a LangChain statemachine graph"""
    chain = await afake_chain()
    node1 = await afake_runnable(chain=chain, name="node1", root=False)
    sequence = await afake_node_sequence(chain=chain, root=False)
    branch = await afake_node_state_machine(
        chain=chain,
        root=True,
        branches=[
            (BranchMeta(name="a", description="the first branch"), node1),
            (BranchMeta(name="b", description="the second branch"), sequence),
        ],
    )

    assert await chain.nodes.filter(root=True).acount() == 1
    return {
        "chain": chain,
        "graph": branch,
        "node1": node1,
        "sequence": sequence,
    }


def _post_process(input: Input, config: dict, state: dict, **kwargs):
    return {"messages": [AIMessage(content="mock statemachine response")]}


POST_PROCESS = "ix.chains.tests.loader.test_langgraph._post_process"


@pytest_asyncio.fixture
async def lcel_graph_with_implicit_join(anode_types, lcel_graph) -> dict:
    """Graph where two branches join implicitly before looping back to the start

    This simulates a common pattern where multiple nodes use the same post-processing
    node at the end of each loop. (e.g. to format response to messages)
    """
    # attach both nodes to a single post-processing node
    node1 = lcel_graph["node1"]
    node2 = lcel_graph["node2"]
    post_process = await afake_runnable(
        value=10,
        chain=lcel_graph["chain"],
        name="post_process",
        root=False,
        config=dict(func_class_path=POST_PROCESS),
    )
    for node in [node1, node2]:
        await afake_chain_edge(
            chain=lcel_graph["chain"],
            source=node,
            target=post_process,
            relation="LINK",
            source_key="out",
            target_key="in",
        )

    # single loop back to the graph
    await afake_chain_edge(
        chain=lcel_graph["chain"],
        source=post_process,
        target=lcel_graph["graph"].node,
        relation="GRAPH",
        source_key="out",
        target_key="loop",
    )

    updated_graph = lcel_graph.copy()
    updated_graph["post_process"] = post_process
    return updated_graph


@pytest.mark.django_db
class TestLoadGraph:
    """Test loading LangGraph state machines"""

    # TODO: test with graph in sequence
    # TODO: test with map in branch
    # TODO: test with branch in branch

    async def test_load_basic(self, lcel_graph, aix_context):
        fixture = lcel_graph
        chain = fixture["chain"]

        # smoke test that node config was created correctly
        assert fixture["graph"].node.config.get("branches", None) == [
            BranchMeta(name="a", description="the first branch"),
            BranchMeta(name="b", description="the second branch"),
        ]

        # sanity check setup
        assert isinstance(fixture["graph"], StateMachinePlaceholder)
        assert fixture["graph"].branches == [
            ("a", fixture["node1"]),
            ("b", fixture["node2"]),
        ]
        assert fixture["graph"].loops == ["a", "b"]
        assert fixture["graph"].entry_point == "start"

        # test loaded flow
        _, flow = await aload_chain_flow(chain)

        assert flow == fixture["graph"]

    async def invoke(
        self, runnable: Runnable, input: Input, config: Optional[RunnableConfig] = None
    ) -> Output:
        # invoke was not returning output. Testing with stream for now.
        # TODO: double check docs for if/how invoke is supposed to work.
        async for output in runnable.astream(input):
            # stream() yields dictionaries with output keyed by node name
            for key, value in output.items():
                print(f"Output from node '{key}':")
                print("---")
                print(value)
            print("\n---\n")
        return output

    async def test_invoke_basic(self, lcel_graph, aix_context):
        fixture = lcel_graph
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)

        inputs = {
            "messages": [
                {"content": "test", "type": "AIMessage"},
            ]
        }
        output = await self.invoke(flow, inputs)

        assert {
            "__end__": {
                "messages": [
                    {"content": "test", "type": "AIMessage"},
                    AIMessage(content="mock statemachine action"),
                ]
            }
        } == output

    async def test_load_sequence_in_graph(self, lcel_sequence_in_graph, aix_context):
        fixture = lcel_sequence_in_graph
        chain = fixture["chain"]

        # sanity check setup
        assert isinstance(fixture["graph"], StateMachinePlaceholder)
        assert fixture["graph"].branches == [
            ("a", fixture["node1"]),
            ("b", fixture["sequence"]),
        ]
        assert fixture["graph"].loops == ["a", "b"]
        assert fixture["graph"].entry_point == "start"

        # test loaded flow
        _, flow = await aload_chain_flow(chain)

        assert flow == fixture["graph"]

    async def test_invoke_sequence_in_graph(self, lcel_sequence_in_graph, aix_context):
        fixture = lcel_sequence_in_graph
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)

        inputs = {
            "messages": [
                {"content": "test", "type": "AIMessage"},
            ]
        }
        output = await self.invoke(flow, inputs)

        assert {
            "__end__": {
                "messages": [
                    {"content": "test", "type": "AIMessage"},
                    AIMessage(content="mock statemachine action"),
                ]
            }
        } == output

    async def test_load_with_end(self, lcel_graph_with_end, aix_context):
        fixture = lcel_graph_with_end
        chain = fixture["chain"]

        # sanity check setup
        assert isinstance(fixture["graph"], StateMachinePlaceholder)
        assert fixture["graph"].branches == [
            ("a", fixture["node1"]),
            ("b", fixture["node2"]),
        ]
        assert fixture["graph"].loops == ["a", "b"]
        assert fixture["graph"].entry_point == "start"
        assert fixture["graph"].ends == ["a"]

        # test loaded flow
        _, flow = await aload_chain_flow(chain)

        assert flow == fixture["graph"]

    async def test_invoke_with_end(self, lcel_graph_with_end, aix_context):
        fixture = lcel_graph_with_end
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)

        inputs = {
            "messages": [
                {"content": "test", "type": "AIMessage"},
            ]
        }
        output = await self.invoke(flow, inputs)

        assert {
            "__end__": {
                "messages": [
                    {"content": "test", "type": "AIMessage"},
                    AIMessage(content="mock statemachine action"),
                ]
            }
        } == output

    async def test_load_with_shared_end(self, lcel_graph_with_shared_end, aix_context):
        fixture = lcel_graph_with_shared_end
        chain = fixture["chain"]

        # sanity check setup
        assert isinstance(fixture["graph"], StateMachinePlaceholder)
        assert fixture["graph"].branches == [
            ("a", fixture["node1"]),
            ("b", fixture["node2"]),
        ]
        assert fixture["graph"].loops == ["a", "b"]
        assert fixture["graph"].entry_point == "start"
        assert fixture["graph"].ends == ["a", "b"]

        # test loaded flow
        _, flow = await aload_chain_flow(chain)

        assert flow == fixture["graph"]

    async def test_invoke_with_shared_end(
        self, lcel_graph_with_shared_end, aix_context
    ):
        fixture = lcel_graph_with_shared_end
        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)

        inputs = {
            "messages": [
                {"content": "test", "type": "AIMessage"},
            ]
        }
        output = await self.invoke(flow, inputs)

        assert {
            "__end__": {
                "messages": [
                    {"content": "test", "type": "AIMessage"},
                    AIMessage(content="mock statemachine action"),
                ]
            }
        } == output

    async def test_load_with_implicit_join(
        self, lcel_graph_with_implicit_join, aix_context
    ):
        fixture = lcel_graph_with_implicit_join
        chain = fixture["chain"]

        # sanity check setup
        assert isinstance(fixture["graph"], StateMachinePlaceholder)
        assert fixture["graph"].branches == [
            ("a", fixture["node1"]),
            ("b", fixture["node2"]),
        ]
        assert fixture["graph"].loops == ["a", "b"]
        assert fixture["graph"].entry_point == "start"
        assert fixture["graph"].ends == []

        # test loaded flow
        _, flow = await aload_chain_flow(chain)

        graph = flow
        assert isinstance(graph, StateMachinePlaceholder)
        assert graph.loops == ["a", "b"]
        assert graph.entry_point == "start"
        assert graph.ends == []

        label_a, branch_a = graph.branches[0]
        assert label_a == "a"
        assert isinstance(branch_a, ImplicitJoin)
        assert branch_a.source == [fixture["node1"]]
        assert branch_a.target.node == fixture["post_process"]

        # branch_b
        label_b, branch_b = graph.branches[1]
        assert label_b == "b"
        assert isinstance(branch_b, ImplicitJoin)
        assert branch_b.source == [fixture["node2"]]
        assert branch_b.target.node == fixture["post_process"]

    async def test_invoke_with_implicit_join(
        self, lcel_graph_with_implicit_join, aix_context
    ):
        """Test invoking a graph with two branches that join implicitly before looping back to the start

        This test simulates a loop, with both branches being called before exiting
        """
        fixture = lcel_graph_with_implicit_join

        chain = fixture["chain"]
        flow = await ainit_chain_flow(chain, context=aix_context)

        inputs = {
            "messages": [
                {"content": "test", "type": "AIMessage"},
            ]
        }
        output = await self.invoke(
            flow, inputs, config={"responses": ["a", "b", "end"]}
        )

        assert {
            "__end__": {
                "messages": [
                    {"content": "test", "type": "AIMessage"},
                    AIMessage(content="mock statemachine action"),
                ]
            }
        } == output
