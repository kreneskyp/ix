import React, { Suspense } from "react";
import { useParams } from "react-router-dom";
import { Box, Center } from "@chakra-ui/react";

import { TaskProvider, useTask } from "tasks/contexts";
import TaskLogMessageStream from "task_log/TaskLogMessageStream";
import FeedbackForm from "task_log/FeedbackInput";
import AutonomousToggle from "chat/AutonomousToggle";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { ScrollableBox } from "site/ScrollableBox";
import TaskLogLeftPane from "task_log/TaskLogLeftPane";

export const TaskLogView = () => {
  const { id } = useParams();

  return (
    <TaskProvider taskId={id}>
      <Layout>
        <LayoutLeftPane>
          <TaskLogLeftPane />
        </LayoutLeftPane>
        <LayoutContent>
          <ScrollableBox>
            <Suspense>
              <TaskLogMessageStream />
            </Suspense>
          </ScrollableBox>
          <Center w="100%" p={4} boxShadow="0px -1px 4px rgba(0, 0, 0, 0.1)">
            {/* Bottom aligned section */}
            <Box mr={10}>
              <FeedbackForm />
            </Box>
            {/* nest another provider here so refresh does not affect the whole view */}
            <Box width={100}>
              <Suspense>
                <TaskProvider taskId={id}>
                  <AutonomousToggle />
                </TaskProvider>
              </Suspense>
            </Box>
          </Center>
        </LayoutContent>
      </Layout>
    </TaskProvider>
  );
};

export default TaskLogView;
