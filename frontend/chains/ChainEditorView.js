import React, { useCallback, useState, useEffect, useMemo } from "react";
import { useParams } from "react-router-dom";
import {
  HStack,
  Spinner,
  useDisclosure,
  useToast,
  VStack,
} from "@chakra-ui/react";
import { ReactFlowProvider, useReactFlow } from "reactflow";

import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import ChainGraphEditor from "chains/ChainGraphEditor";
import { ChainGraphEditorSideBar } from "chains/editor/ChainGraphEditorSideBar";
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

const ChainEditorProvider = ({ graph, onError, children }) => {
  const reactFlowInstance = useReactFlow();
  const api = useChainEditorAPI({
    chain: graph?.chain,
    reactFlowInstance,
    onError,
  });
  const chainState = useChainState(graph);
  const nodeState = useNodeState(graph?.chain, graph?.nodes);
  const selectedNode = useSelectedNode();
  const nodeEditor = useNodeEditorState(
    selectedNode,
    nodeState.nodes,
    nodeState.setNode
  );

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
  const graph = response?.data;
  const toast = useToast();

  const rightSidebarDisclosure = useDisclosure({ defaultIsOpen: true });

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
    content = (
      <ChainGraphEditor
        key={idRef}
        rightSidebarDisclosure={rightSidebarDisclosure}
      />
    );
  } else if (isLoading || !graph) {
    content = <Spinner />;
  } else {
    content = (
      <ChainGraphEditor
        graph={graph}
        rightSidebarDisclosure={rightSidebarDisclosure}
      />
    );
  }

  return (
    <ReactFlowProvider>
      <ChainEditorProvider graph={graph} onError={onAPIError}>
        <Layout>
          <LayoutLeftPane>
            <ChainGraphEditorSideBar />
          </LayoutLeftPane>
          <LayoutContent>
            <HStack>
              <VStack alignItems="start" p={5} spacing={4}>
                {content}
              </VStack>
              <EditorRightSidebar {...rightSidebarDisclosure} />
            </HStack>
          </LayoutContent>
        </Layout>
      </ChainEditorProvider>
    </ReactFlowProvider>
  );
};
