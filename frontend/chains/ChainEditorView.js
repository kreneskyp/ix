import React from "react";
import { useParams } from "react-router-dom";
import { Spinner, VStack } from "@chakra-ui/react";

import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import ChainGraphEditor from "chains/ChainGraphEditor";
import { ChainGraphEditorSideBar } from "chains/editor/ChainGraphEditorSideBar";
import { useDetailAPI } from "utils/hooks/useDetailAPI";
import { useObjectEditorView } from "utils/hooks/useObjectEditorView";

export const ChainEditorView = () => {
  const { id } = useParams();
  const { response, call, isLoading } = useDetailAPI(`/api/chains/${id}/graph`);
  const { isNew, idRef } = useObjectEditorView(id, call);
  const graph = response?.data;

  let content;
  if (isNew) {
    content = <ChainGraphEditor key={idRef} />;
  } else if (isLoading || !graph) {
    content = <Spinner />;
  } else {
    content = <ChainGraphEditor graph={graph} />;
  }

  return (
    <Layout>
      <LayoutLeftPane>
        <ChainGraphEditorSideBar />
      </LayoutLeftPane>
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          {content}
        </VStack>
      </LayoutContent>
    </Layout>
  );
};
