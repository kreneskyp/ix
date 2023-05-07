import React, { Suspense, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Box, Center, HStack, Spinner, VStack } from "@chakra-ui/react";

import { TaskProvider } from "tasks/contexts";
import TaskLogMessageStream from "task_log/TaskLogMessageStream";
import FeedbackForm from "task_log/FeedbackInput";
import AutonomousToggle from "chat/AutonomousToggle";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { ScrollableBox } from "site/ScrollableBox";
import RunButton from "chat/RunButton";
import { useQueryLoader } from "react-relay";
import { ChatByIdQuery } from "chat/graphql/ChatByIdQuery";
import { usePreloadedQuery } from "react-relay/hooks";
import { AgentProvider } from "agents/graphql/AgentProvider";
import AgentCardModalButton from "agents/AgentCardModalButton";
import SideBarPlanList from "chat/SideBarPlanList";
import SideBarArtifactList from "chat/sidebar/SideBarArtifactList";

export const ChatContentShim = ({ queryRef }) => {
  const { chat } = usePreloadedQuery(ChatByIdQuery, queryRef);
  const moderatorTask = chat.task;

  return (
    <>
      <ScrollableBox>
        <Suspense>
          <TaskProvider taskId={moderatorTask.id}>
            <TaskLogMessageStream />
          </TaskProvider>
        </Suspense>
      </ScrollableBox>
      <Center w="100%" p={4} boxShadow="0px -1px 4px rgba(0, 0, 0, 0.1)">
        {/* Bottom aligned section */}
        <Box mr={10}>
          <TaskProvider taskId={moderatorTask.id}>
            <FeedbackForm />
          </TaskProvider>
        </Box>
        {/* nest another provider here so refresh does not affect the whole view */}
        <Box width={100}>
          <Suspense>
            <TaskProvider taskId={moderatorTask.id}>
              <HStack>
                <RunButton />
                <AutonomousToggle />
              </HStack>
            </TaskProvider>
          </Suspense>
        </Box>
      </Center>
    </>
  );
};

export const ChatLeftPaneShim = ({ queryRef }) => {
  const { chat } = usePreloadedQuery(ChatByIdQuery, queryRef);
  const moderatorTask = chat.task;

  return (
    <Suspense>
      <VStack spacing={4} align="stretch">
        <AgentProvider agentId={chat.lead.id}>
          <AgentCardModalButton />
        </AgentProvider>
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
  }, []);

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
