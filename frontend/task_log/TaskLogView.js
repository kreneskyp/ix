import React, { Suspense } from "react";
import { useParams } from "react-router-dom";
import { Box, Center, HStack } from "@chakra-ui/react";

import { TaskProvider } from "tasks/contexts";
import TaskLogMessageStream from "task_log/TaskLogMessageStream";
import ChatInput from "chat/ChatInput";
import AutonomousToggle from "chat/AutonomousToggle";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { ScrollableBox } from "site/ScrollableBox";
import TaskLogLeftPane from "task_log/TaskLogLeftPane";
import RunButton from "chat/RunButton";

export const TaskLogView = () => {
  const { id } = useParams();

  return (
    <Layout>
      <LayoutLeftPane>
        <Suspense>
          <TaskProvider taskId={id}>
            <TaskLogLeftPane />
          </TaskProvider>
        </Suspense>
      </LayoutLeftPane>
      <LayoutContent>
        <ScrollableBox>
          <Suspense>
            <TaskProvider taskId={id}>
              <TaskLogMessageStream />
            </TaskProvider>
          </Suspense>
        </ScrollableBox>
        <Center w="100%" p={4} boxShadow="0px -1px 4px rgba(0, 0, 0, 0.1)">
          {/* Bottom aligned section */}
          <Box mr={10}>
            <TaskProvider taskId={id}>
              <ChatInput />
            </TaskProvider>
          </Box>
          {/* nest another provider here so refresh does not affect the whole view */}
          <Box width={100}>
            <Suspense>
              <TaskProvider taskId={id}>
                <HStack>
                  <RunButton />
                  <AutonomousToggle />
                </HStack>
              </TaskProvider>
            </Suspense>
          </Box>
        </Center>
      </LayoutContent>
    </Layout>
  );
};

export default TaskLogView;
