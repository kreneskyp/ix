import React, { useEffect, useCallback } from "react";
import { useQueryLoader } from "react-relay";
import { ChatHistoryQuery } from "chat/graphql/ChatHistoryQuery";
import { ChatTable } from "chat/history/ChatTable";
import { Heading, Spinner, VStack } from "@chakra-ui/react";
import { Layout, LayoutContent } from "site/Layout";

export const ChatHistoryView = () => {
  const [queryRef, loadQuery] = useQueryLoader(ChatHistoryQuery);

  const load = useCallback((limit = 10, offset = 0) => {
    loadQuery({ limit, offset }, { fetchPolicy: "store-and-network" });
  });

  useEffect(() => {
    load();
  }, []);

  if (!queryRef) {
    return <Spinner />;
  }

  return (
    <Layout>
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          <Heading>Chats</Heading>
          <ChatTable queryRef={queryRef} load={load} />
        </VStack>
      </LayoutContent>
    </Layout>
  );
};

export default ChatHistoryView;
