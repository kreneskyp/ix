import React from "react";
import { Box, Center, Flex, VStack } from "@chakra-ui/react";
import { TaskLogMessageStream } from "task_log/TaskLogMessageStream";
import { TaskResponseForm } from "task_log/TaskResponseForm";
import { useTask } from "tasks/contexts";
import { TaskLogProvider } from "task_log/contexts";

export const TaskLogCenterPane = () => {
  const { task } = useTask();

  return (
    <TaskLogProvider taskId={task.id}>
      <Flex direction="column" h="100vh">
        <Box flex="1">
          <VStack spacing={4} align="stretch">
            <TaskLogMessageStream />
          </VStack>
        </Box>
        <Box p={4}>
          <Center>
            <Box maxW="lg" w="100%" mx={2} my={8}>
              <TaskResponseForm />
            </Box>
          </Center>
        </Box>
      </Flex>
    </TaskLogProvider>
  );
};

export default TaskLogCenterPane;
