import React, { useEffect } from "react";
import { usePreloadedQuery } from "react-relay/hooks";
import { useQueryLoader } from "react-relay";
import { useParams } from "react-router-dom";
import { Heading, Spinner, VStack } from "@chakra-ui/react";

import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import ChainGraph from "chains/ChainGraph";
import { ChainGraphByIdQuery } from "chains/graphql/ChainGraphByIdQuery";
import ChainGraphEditor from "chains/ChainGraphEditor";
import { ChainGraphEditorSideBar } from "chains/editor/ChainGraphEditorSideBar";

const ChainEditorShim = ({ queryRef }) => {
  const { graph } = usePreloadedQuery(ChainGraphByIdQuery, queryRef);
  return (
    <>
      <Heading>{graph.chain.name}</Heading>
      <ChainGraph graph={graph} />;
    </>
  );
};

export const ChainEditorView = () => {
  const { id } = useParams();
  let content;
  let leftPane;
  if (id !== undefined && id !== null) {
    const [queryRef, loadQuery] = useQueryLoader(ChainGraphByIdQuery);

    useEffect(() => {
      loadQuery({ id }, { fetchPolicy: "network-only" });
    }, []);

    if (!queryRef) {
      content = <Spinner />;
    } else {
      content = <ChainEditorShim queryRef={queryRef} />;
    }
  } else {
    content = <ChainGraphEditor />;
    leftPane = <ChainGraphEditorSideBar />;
  }

  return (
    <Layout>
      <LayoutLeftPane>{leftPane}</LayoutLeftPane>
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          {content}
        </VStack>
      </LayoutContent>
    </Layout>
  );
};

ChainEditorView.defaultProps = {
  chainId: null,
};
