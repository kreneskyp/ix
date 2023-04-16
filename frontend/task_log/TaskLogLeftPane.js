import React from "react";
import { VStack, StackDivider, Box } from "@chakra-ui/react";
import SideBarGoalList from "task_log/SideBarGoalList";
import { ColorModeButton } from "components/ColorModeButton";

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
