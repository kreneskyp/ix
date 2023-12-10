import React, { useCallback, useEffect } from "react";
import { useParams } from "react-router-dom";
import { HStack, Spinner, useToast, VStack } from "@chakra-ui/react";
import { ReactFlowProvider, useReactFlow } from "reactflow";

import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import ChainGraphEditor from "chains/ChainGraphEditor";
import { useDetailAPI } from "utils/hooks/useDetailAPI";
import { useObjectEditorView } from "utils/hooks/useObjectEditorView";
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
} from "chains/editor/contexts";
import { EditorRightSidebar } from "chains/editor/EditorRightSidebar";
import { useNodeState } from "chains/hooks/useNodeState";
import { useChainState } from "chains/hooks/useChainState";
import { NodeTypeSearchButton } from "chains/editor/NodeTypeSearchButton";
import { AgentCardListButton } from "agents/AgentCardListButton";
import { EditorAgentCard } from "chains/editor/sidebar/EditorAgentCard";
import { ChainCardListButton } from "chains/ChainCardListButton";

const ChainEditorProvider = ({ graph, onError, children }) => {
  const chainState = useChainState(graph);
  const nodeState = useNodeState(graph?.chain, graph?.nodes);
  const selectedNode = useSelectedNode();
  const nodeEditor = useNodeEditorState(
    selectedNode,
    nodeState.nodes,
    nodeState.setNode
  );

  const reactFlowInstance = useReactFlow();
  const api = useChainEditorAPI({
    chain: graph?.chain,
    reactFlowInstance,
    onError,
  });

  useEffect(() => {
    if (graph?.chain?.id !== chainState?.chain?.id) {
      chainState.setChain(graph?.chain);
    }
  }, [graph?.chain?.id, chainState.chain]);

  return (
    <ChainState.Provider value={chainState}>
      <NodeStateContext.Provider value={nodeState}>
        <NodeEditorContext.Provider value={nodeEditor}>
          <SelectedNodeContext.Provider value={selectedNode}>
            <ChainEditorAPIContext.Provider value={api}>
              {children}
            </ChainEditorAPIContext.Provider>
          </SelectedNodeContext.Provider>
        </NodeEditorContext.Provider>
      </NodeStateContext.Provider>
    </ChainState.Provider>
  );
};

export const ChainEditorView = () => {
  const { id } = useParams();
  const { response, call, isLoading } = useDetailAPI(`/api/chains/${id}/graph`);
  const { isNew, idRef } = useObjectEditorView(id, call);
  const toast = useToast();

  // Defer to isNew to determine if graph response is current for
  // UX state. This is necessary because the graph response is not cleared when
  // switching to a new chain. Also check that the id matches the response id.
  // to avoid rendering stale state when first loading a newly created chain.
  const graph =
    isNew || id !== response?.data?.chain?.id ? null : response?.data;

  const onAPIError = useCallback((err) => {
    toast({
      title: "Error",
      description: `Failed to save chain. ${err.message}`,
      status: "error",
      duration: 10000,
      isClosable: true,
    });
  }, []);

  let content;
  if (isNew) {
    content = <ChainGraphEditor key={idRef} />;
  } else if (isLoading || !graph) {
    content = <Spinner />;
  } else {
    content = <ChainGraphEditor graph={graph} />;
  }

  return (
    <ReactFlowProvider>
      <ChainEditorProvider graph={graph} onError={onAPIError}>
        <Layout>
          <LayoutLeftPane>
            <AgentCardListButton Card={EditorAgentCard} />
            <ChainCardListButton />
            <NodeTypeSearchButton />
          </LayoutLeftPane>
          <LayoutContent>
            <HStack>
              <VStack
                alignItems="start"
                pl={0}
                pr={2}
                pt={5}
                pb={2}
                spacing={4}
              >
                {content}
              </VStack>
              <EditorRightSidebar />
            </HStack>
          </LayoutContent>
        </Layout>
      </ChainEditorProvider>
    </ReactFlowProvider>
  );
};
