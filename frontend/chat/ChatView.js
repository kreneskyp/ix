import React, { Suspense, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Box, Center, Spinner, VStack } from "@chakra-ui/react";
import { usePreloadedQuery } from "react-relay/hooks";

import { TaskProvider } from "tasks/contexts";
import ChatInput from "chat/ChatInput";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { ScrollableBox } from "site/ScrollableBox";
import { useQueryLoader } from "react-relay";
import { ChatByIdQuery } from "chat/graphql/ChatByIdQuery";
import { useMessageStream } from "chat/graphql/useMessageStream";
import SideBarPlanList from "chat/SideBarPlanList";
import SideBarArtifactList from "chat/sidebar/SideBarArtifactList";
import SideBarAgentList from "chat/sidebar/SideBarAgentList";
import ChatMessages from "chat/ChatMessages";

import {
  MessagesContext,
  SubscriptionActiveContext,
} from "chat/graphql/useChatMessageSubscription";

export const ChatContentShim = ({ queryRef }) => {
  const { chat } = usePreloadedQuery(ChatByIdQuery, queryRef);
  const moderatorTask = chat.task;
  const { messages, subscriptionActive } = useMessageStream(chat);

  return (
    <MessagesContext.Provider value={messages}>
      <SubscriptionActiveContext.Provider value={subscriptionActive}>
        <ScrollableBox>
          <Suspense>
            <TaskProvider taskId={moderatorTask.id}>
              <ChatMessages chat={chat} />
            </TaskProvider>
          </Suspense>
        </ScrollableBox>
        <Center
          w="100%"
          p={4}
          mb={4}
          boxShadow="0px -1px 4px rgba(0, 0, 0, 0.1)"
        >
          {/* Bottom aligned section */}
          <Box mr={10}>
            <TaskProvider taskId={moderatorTask.id}>
              <ChatInput chat={chat} />
            </TaskProvider>
          </Box>
        </Center>
      </SubscriptionActiveContext.Provider>
    </MessagesContext.Provider>
  );
};

export const ChatLeftPaneShim = ({ queryRef }) => {
  const { chat } = usePreloadedQuery(ChatByIdQuery, queryRef);
  const moderatorTask = chat.task;

  return (
    <Suspense>
      <VStack spacing={4} align="stretch">
        <SideBarAgentList queryRef={queryRef} />
        <SideBarPlanList queryRef={queryRef} />
        <SideBarArtifactList queryRef={queryRef} />
      </VStack>
    </Suspense>
  );
};

export const ChatView = () => {
  const { id } = useParams();
  const [queryRef, loadQuery] = useQueryLoader(ChatByIdQuery);

  useEffect(() => {
    loadQuery({ id }, { fetchPolicy: "network-only" });
  }, [id]);

  return (
    <Layout>
      <LayoutLeftPane>
        {!queryRef ? <Spinner /> : <ChatLeftPaneShim queryRef={queryRef} />}
      </LayoutLeftPane>
      <LayoutContent>
        {!queryRef ? <Spinner /> : <ChatContentShim queryRef={queryRef} />}
      </LayoutContent>
    </Layout>
  );
};
