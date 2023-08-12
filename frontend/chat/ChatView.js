import React, { Suspense, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Box, Center, Spinner, VStack } from "@chakra-ui/react";

import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { ScrollableBox } from "site/ScrollableBox";
import { useMessageStream } from "chat/graphql/useMessageStream";
import SideBarPlanList from "chat/SideBarPlanList";
import SideBarArtifactList from "chat/sidebar/SideBarArtifactList";
import SideBarAgentList from "chat/sidebar/SideBarAgentList";
import ChatMessages from "chat/ChatMessages";

import {
  MessagesContext,
  SubscriptionActiveContext,
} from "chat/graphql/useChatMessageSubscription";
import ChatInput from "chat/input/ChatInput";
import { MessagesTokenContext } from "chat/graphql/useChatMessageTokenSubscription";
import { useDetailAPI } from "utils/hooks/useDetailAPI";

export const ChatContentShim = ({ graph }) => {
  const { messages, streams, subscriptionActive } = useMessageStream(
    graph.chat
  );

  return (
    <MessagesTokenContext.Provider value={streams}>
      <MessagesContext.Provider value={messages}>
        <SubscriptionActiveContext.Provider value={subscriptionActive}>
          <ScrollableBox>
            <Suspense>
              <ChatMessages chat={graph.chat} />
            </Suspense>
          </ScrollableBox>
          <Center
            w="100%"
            p={4}
            mb={4}
            boxShadow="0px -1px 4px rgba(0, 0, 0, 0.1)"
          >
            {/* Bottom aligned section */}
            <Box ml={95}>
              <ChatInput chat={graph.chat} />
            </Box>
          </Center>
        </SubscriptionActiveContext.Provider>
      </MessagesContext.Provider>
    </MessagesTokenContext.Provider>
  );
};

export const ChatLeftPaneShim = ({ graph, loadGraph }) => {
  return (
    <Suspense>
      <VStack spacing={4} align="stretch">
        <SideBarAgentList graph={graph} loadGraph={loadGraph} />
        <SideBarPlanList plans={graph.plans} />
        <SideBarArtifactList chat={graph.chat} artifacts={graph.artifacts} />
      </VStack>
    </Suspense>
  );
};

export const useChatGraph = (id) => {
  return useDetailAPI(`/api/chats/${id}/graph`);
};

export const ChatView = () => {
  const { id } = useParams();
  const { response, call: loadGraph, isLoading } = useChatGraph(id);
  const graph = response?.data;

  useEffect(() => {
    loadGraph();
  }, [id]);

  return (
    <Layout>
      <LayoutLeftPane>
        {isLoading || !graph ? (
          <Spinner />
        ) : (
          <ChatLeftPaneShim graph={graph} loadGraph={loadGraph} />
        )}
      </LayoutLeftPane>
      <LayoutContent>
        {isLoading || !graph ? <Spinner /> : <ChatContentShim graph={graph} />}
      </LayoutContent>
    </Layout>
  );
};
