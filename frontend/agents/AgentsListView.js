import React from "react";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { AgentCardList } from "agents/AgentCardList";
import { Heading, Spinner, VStack } from "@chakra-ui/react";
import { ScrollableBox } from "site/ScrollableBox";
import { NewAgentButton } from "agents/NewAgentButton";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { useLocation } from "react-router-dom";

export const AgentsListView = () => {
  const location = useLocation();
  const { page, isLoading } = usePaginatedAPI("/api/agents/", {
    loadDependencies: [location],
  });

  return (
    <Layout>
      <LayoutLeftPane>
        <NewAgentButton />
      </LayoutLeftPane>
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          <Heading>Agents</Heading>
          <ScrollableBox>
            {isLoading ? <Spinner /> : <AgentCardList page={page} />}
          </ScrollableBox>
        </VStack>
      </LayoutContent>
    </Layout>
  );
};
