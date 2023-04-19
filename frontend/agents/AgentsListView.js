import React, { useEffect } from "react";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { AgentCardList } from "agents/AgentCardList";
import { AgentsQuery } from "agents/graphql/AgentsQuery";
import { useQueryLoader } from "react-relay";
import { Heading, Spinner, VStack } from "@chakra-ui/react";
import { ScrollableBox } from "site/ScrollableBox";

export const AgentsListView = () => {
  const [queryRef, loadQuery] = useQueryLoader(AgentsQuery);

  useEffect(() => {
    loadQuery({}, { fetchPolicy: "network-only" });
  }, []);

  let content;
  if (!queryRef) {
    return <Spinner />;
  } else {
    content = <AgentCardList queryRef={queryRef} />;
  }

  return (
    <Layout>
      <LayoutLeftPane />
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          <Heading>Agents</Heading>
          <ScrollableBox>{content}</ScrollableBox>
        </VStack>
      </LayoutContent>
    </Layout>
  );
};
