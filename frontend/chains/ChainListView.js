import React, { useEffect } from "react";
import { useQueryLoader } from "react-relay";
import { Heading, Spinner, VStack } from "@chakra-ui/react";
import { ScrollableBox } from "site/ScrollableBox";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";

import { ChainsQuery } from "chains/graphql/ChainsQuery";
import { ChainCardList } from "chains/ChainCardList";
import { NewChainButton } from "chains/NewChainButton";

export const ChainListView = () => {
  const [queryRef, loadQuery] = useQueryLoader(ChainsQuery);

  useEffect(() => {
    loadQuery({}, { fetchPolicy: "network-only" });
  }, []);

  let content;
  if (!queryRef) {
    return <Spinner />;
  } else {
    content = <ChainCardList queryRef={queryRef} />;
  }

  return (
    <Layout>
      <LayoutLeftPane>
        <NewChainButton />
      </LayoutLeftPane>
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          <Heading>Chains</Heading>
          <ScrollableBox>{content}</ScrollableBox>
        </VStack>
      </LayoutContent>
    </Layout>
  );
};
