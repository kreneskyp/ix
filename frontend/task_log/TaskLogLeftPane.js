import React from "react";
import { VStack, StackDivider, Box } from "@chakra-ui/react";
import TaskPlan from "task_log/TaskPlan";
import SideBarGoalList from "task_log/SideBarGoalList";

export const TaskLogLeftPane = () => {
  return (
    <Box pl={4} pr={4}>
      <VStack
        divider={<StackDivider borderColor="gray.200" />}
        spacing={4}
        align="stretch"
      >
        <SideBarGoalList />
        <TaskPlan />
      </VStack>
    </Box>
  );
};

export default TaskLogLeftPane;
