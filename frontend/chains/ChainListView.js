import React from "react";
import { Heading, Spinner, VStack } from "@chakra-ui/react";
import { ScrollableBox } from "site/ScrollableBox";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";

import { ChainCardList } from "chains/ChainCardList";
import { NewChainButton } from "chains/NewChainButton";
import { useLocation } from "react-router-dom";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";

export const ChainListView = () => {
  const location = useLocation();
  const { page, isLoading } = usePaginatedAPI("/api/chains/", {
    loadDependencies: [location],
    limit: 90000,
  });

  return (
    <Layout>
      <LayoutLeftPane>
        <NewChainButton />
      </LayoutLeftPane>
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          <Heading>Chains</Heading>
          <ScrollableBox>
            {isLoading ? <Spinner /> : <ChainCardList page={page} />}
          </ScrollableBox>
        </VStack>
      </LayoutContent>
    </Layout>
  );
};
