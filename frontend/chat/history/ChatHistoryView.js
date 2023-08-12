import React from "react";
import { ChatTable } from "chat/history/ChatTable";
import { Heading, Spinner, VStack } from "@chakra-ui/react";
import { Layout, LayoutContent } from "site/Layout";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";

export const ChatHistoryView = () => {
  const { page, load, isLoading } = usePaginatedAPI("/api/chats/");

  return (
    <Layout>
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          <Heading>Chats</Heading>
          {isLoading ? <Spinner /> : <ChatTable page={page} load={load} />}
        </VStack>
      </LayoutContent>
    </Layout>
  );
};
