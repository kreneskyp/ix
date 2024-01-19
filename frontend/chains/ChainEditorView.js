import React, { useCallback } from "react";
import { useParams } from "react-router-dom";
import { HStack, Spinner, useToast, VStack } from "@chakra-ui/react";
import { ReactFlowProvider, useReactFlow } from "reactflow";

import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import ChainGraphEditor from "chains/ChainGraphEditor";
import { useChainEditorAPI } from "chains/hooks/useChainEditorAPI";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import {
  useNodeEditorState,
  useSelectedNode,
} from "chains/hooks/useSelectedNode";
import {
  SelectedNodeContext,
  NodeStateContext,
  NodeEditorContext,
  ChainState,
  ChainTypes,
} from "chains/editor/contexts";
import { EditorRightSidebar } from "chains/editor/EditorRightSidebar";
import { NodeTypeSearchButton } from "chains/editor/NodeTypeSearchButton";
import { AgentCardListButton } from "agents/AgentCardListButton";
import { EditorAgentCard } from "chains/editor/sidebar/EditorAgentCard";
import { ChainCardListButton } from "chains/ChainCardListButton";
import { RunLogProvider } from "chains/editor/run_log/RunLogProvider";
import { RunLogMenuButton } from "chains/editor/run_log/RunLogMenuButton";
import { EditorTopBar } from "chains/editor/EditorTopBar";
import { useNodeState } from "chains/hooks/useNodeState";
import { useTabState, TabState } from "chains/hooks/useTabState";
import { useTabDataField } from "chains/hooks/useTabDataField";
export const EditorViewState = React.createContext(null);

/**
 * Init state for the editor and it's tabs. This is the top level state that manages
 * state for a tabs.
 *
 * Each tab's state is stored generically in the tab. This hook provides flow
 * editor specific state on top of that.
 */
export const useEditorTabs = (initial) => {
  const tabState = useTabState(initial);

  const openChain = React.useCallback(
    async (chain_id) => {
      const response = await fetch(`/api/chains/${chain_id}/graph`).then(
        (res) => res.json()
      );
      const graph = response?.chain?.id ? response : null;

      const nodes = {};
      graph?.nodes?.forEach((node) => {
        nodes[node.id] = node;
      });

      tabState.addTab({
        chain_id: chain_id,
        chain: graph.chain,
        edges: graph.edges,
        types: graph.types,
        nodes,
      });
      tabState.setIndex(tabState.state.length);
    },
    [tabState.addTab]
  );

  const addChain = React.useCallback(
    async (chain) => {
      tabState.addTab({
        chain_id: null,
        chain: chain || {},
        edges: [],
        types: [],
        nodes: {},
      });
    },
    [tabState.addTab]
  );

  const selectOrOpenChain = React.useCallback(
    async (chain_id) => {
      if (tabState.state.some((tab) => tab.chain_id === chain_id)) {
        tabState.setIndex(
          tabState.state.findIndex((tab) => tab.chain_id === chain_id)
        );
      } else {
        await openChain(chain_id).catch((err) => {
          console.error("Failed to open chain", err);
        });
      }
    },
    [tabState.state, openChain]
  );

  const closeChain = React.useCallback((chain_id) => {
    tabState.removeTab(
      tabState.state.findIndex((tab) => tab.chain_id === chain_id)
    );
  }, []);

  return {
    tabState,
    typeState: useTabDataField(tabState.active, tabState.setActive, "types"),
    chainState: useTabDataField(tabState.active, tabState.setActive, "chain"),
    nodeState: useNodeState(tabState),
    selection: useSelectedNode(tabState),
    addChain,
    openChain,
    selectOrOpenChain,
    closeChain,
  };
};

const ChainEditorProvider = ({ onError, children }) => {
  const { chainState, typeState, nodeState, selection } =
    React.useContext(EditorViewState);

  const nodeEditor = useNodeEditorState(
    selection?.node,
    nodeState?.nodes,
    nodeState?.setNode
  );

  const reactFlowInstance = useReactFlow();

  const api = useChainEditorAPI({
    reactFlowInstance,
    onError,
  });

  return (
    <ChainTypes.Provider value={typeState}>
      <ChainState.Provider value={chainState}>
        <NodeStateContext.Provider value={nodeState}>
          <NodeEditorContext.Provider value={nodeEditor}>
            <SelectedNodeContext.Provider value={selection}>
              <ChainEditorAPIContext.Provider value={api}>
                <RunLogProvider chain_id={chainState?.[0]?.id}>
                  {children}
                </RunLogProvider>
              </ChainEditorAPIContext.Provider>
            </SelectedNodeContext.Provider>
          </NodeEditorContext.Provider>
        </NodeStateContext.Provider>
      </ChainState.Provider>
    </ChainTypes.Provider>
  );
};

export const ChainEditorControl = () => {
  const { id } = useParams();
  const toast = useToast();

  const editorTabs = useEditorTabs();

  React.useEffect(() => {
    if (id) {
      editorTabs.openChain(id);
    } else {
      editorTabs.addChain();
    }
  }, [id]);

  const onAPIError = useCallback((err) => {
    toast({
      title: "Error",
      description: `Failed to save chain. ${err.message}`,
      status: "error",
      duration: 10000,
      isClosable: true,
    });
  }, []);

  return (
    <EditorViewState.Provider value={editorTabs}>
      <TabState.Provider value={editorTabs.tabState}>
        <ChainEditorTab onError={onAPIError} />
      </TabState.Provider>
    </EditorViewState.Provider>
  );
};

export const ChainEditorView = () => {
  return (
    <ReactFlowProvider>
      <ChainEditorControl />
    </ReactFlowProvider>
  );
};

export const ChainEditorTab = ({ onError }) => {
  const { active } = React.useContext(TabState);
  const isLoading = false;

  let content;
  if (isLoading || !active) {
    content = <Spinner />;
  } else if (active.chain_id === undefined || active.chain_id === null) {
    // HAX: need to set key here to differentiate between tab
    content = <ChainGraphEditor key={"key"} />;
  } else {
    content = <ChainGraphEditor graph={active} />;
  }

  return (
    <ChainEditorProvider onError={onError}>
      <Layout>
        <LayoutLeftPane>
          <AgentCardListButton Card={EditorAgentCard} />
          <ChainCardListButton />
          <NodeTypeSearchButton />
          <RunLogMenuButton />
        </LayoutLeftPane>
        <LayoutContent>
          <HStack>
            <VStack alignItems="start" pl={0} pr={2} pb={2} spacing={4}>
              <EditorTopBar />
              {content}
            </VStack>
            <EditorRightSidebar />
          </HStack>
        </LayoutContent>
      </Layout>
    </ChainEditorProvider>
  );
};
