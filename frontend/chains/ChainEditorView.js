import React, { useCallback, useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { HStack, Spinner, useToast, VStack } from "@chakra-ui/react";
import { ReactFlowProvider, useReactFlow } from "reactflow";

import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import ChainGraphEditor from "chains/ChainGraphEditor";
import { ChainGraphEditorSideBar } from "chains/editor/ChainGraphEditorSideBar";
import { useDetailAPI } from "utils/hooks/useDetailAPI";
import { useObjectEditorView } from "utils/hooks/useObjectEditorView";
import { useChainEditorAPI } from "chains/hooks/useChainEditorAPI";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import { useSelectedNode } from "chains/hooks/useSelectedNode";
import { SelectedNodeContext } from "chains/editor/SelectedNodeContext";

const ChainEditorProvider = ({ chain, onError, children }) => {
  const reactFlowInstance = useReactFlow();
  const api = useChainEditorAPI({
    chain,
    reactFlowInstance,
    onError,
  });
  const selectedNode = useSelectedNode();

  return (
    <SelectedNodeContext.Provider value={selectedNode}>
      <ChainEditorAPIContext.Provider value={api}>
        {children}
      </ChainEditorAPIContext.Provider>
    </SelectedNodeContext.Provider>
  );
};

export const ChainEditorView = () => {
  const { id } = useParams();
  const { response, call, isLoading } = useDetailAPI(`/api/chains/${id}/graph`);
  const { isNew, idRef } = useObjectEditorView(id, call);
  const graph = response?.data;
  const [chain, setChain] = useState(graph?.chain);
  const toast = useToast();

  const onAPIError = useCallback((err) => {
    toast({
      title: "Error",
      description: `Failed to save chain. ${err.message}`,
      status: "error",
      duration: 10000,
      isClosable: true,
    });
  }, []);

  useEffect(() => {
    setChain(graph?.chain);
  }, [graph?.chain]);

  let content;
  if (isNew) {
    content = <ChainGraphEditor key={idRef} />;
  } else if (isLoading || !graph) {
    content = <Spinner />;
  } else {
    content = (
      <ChainGraphEditor graph={graph} chain={chain} setChain={setChain} />
    );
  }

  return (
    <ReactFlowProvider>
      <ChainEditorProvider chain={chain} onError={onAPIError}>
        <Layout>
          <LayoutLeftPane>
            <ChainGraphEditorSideBar />
          </LayoutLeftPane>
          <LayoutContent>
            <HStack>
              <VStack alignItems="start" p={5} spacing={4}>
                {content}
              </VStack>
            </HStack>
          </LayoutContent>
        </Layout>
      </ChainEditorProvider>
    </ReactFlowProvider>
  );
};
