import React, { Suspense } from "react";
import { useParams } from "react-router-dom";
import { Box, Flex, VStack, Center, Grid } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";

import TaskLogLeftPane from "task_log/TaskLogLeftPane";
import { TaskProvider, useTask } from "tasks/contexts";
import TaskLogMessageStream from "task_log/TaskLogMessageStream";
import FeedbackForm from "task_log/FeedbackInput";
import AutonomousToggle from "chat/AutonomousToggle";

export const TaskLogView = () => {
  const { id } = useParams();
  const { colorMode } = useColorMode();

  return (
    <TaskProvider taskId={id}>
      <Flex h="100vh">
        <VStack
          bg={colorMode === "light" ? "blackAlpha.900" : "blackAlpha.600"}
          w="20%"
          p={4}
          minH="100vh"
        >
          <TaskLogLeftPane />
        </VStack>
        <Flex direction="column" flex="1" h="100%">
          <Box flexGrow="1" overflowY="auto">
            <Grid h="100%" templateRows="1fr auto" alignItems="end" gap={4}>
              <VStack spacing={4} ml={4} mr={4}>
                {/* Scrollable content */}
                <TaskLogMessageStream />
              </VStack>
            </Grid>
          </Box>
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
        </Flex>
      </Flex>
    </TaskProvider>
  );
};

export default TaskLogView;
