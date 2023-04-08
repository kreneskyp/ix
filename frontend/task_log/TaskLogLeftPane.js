import React from "react";
import { VStack, StackDivider } from "@chakra-ui/react";
import TaskGoals from "task_log/TaskGoals";
import TaskPlan from "task_log/TaskPlan";

export const TaskLogLeftPane = () => {
  return (
    <VStack
      divider={<StackDivider borderColor="gray.200" />}
      spacing={4}
      align="stretch"
    >
      <TaskGoals />
      <TaskPlan />
    </VStack>
  );
};

export default TaskLogLeftPane;
