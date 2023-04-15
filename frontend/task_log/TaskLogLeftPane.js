import React from "react";
import { VStack, StackDivider, Box, Flex } from "@chakra-ui/react";
import TaskPlan from "task_log/TaskPlan";
import SideBarGoalList from "task_log/SideBarGoalList";
import { ColorModeToggleButton } from "components/ColorModeToggleButton";
import { ColorModeButton } from "components/ColorMode";

export const TaskLogLeftPane = () => {
  return (
    <Box pl={4} pr={4}>
      <VStack divider={<StackDivider />} spacing={4} align="stretch">
        <SideBarGoalList />
        <ColorModeButton />
      </VStack>
    </Box>
  );
};

export default TaskLogLeftPane;
