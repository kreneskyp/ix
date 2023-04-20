import React from "react";
import { VStack, StackDivider, Box } from "@chakra-ui/react";
import SideBarGoalList from "task_log/SideBarGoalList";
import { AgentProvider } from "agents/graphql/AgentProvider";
import { useTask } from "tasks/contexts";
import AgentCardModalButton from "agents/AgentCardModalButton";

export const TaskLogLeftPane = () => {
  const { task } = useTask();
  return (
    <Box>
      <VStack divider={<StackDivider />} spacing={4} align="stretch">
        <SideBarGoalList />
        <AgentProvider agentId={task.agent.id}>
          <AgentCardModalButton />
        </AgentProvider>
      </VStack>
    </Box>
  );
};

export default TaskLogLeftPane;
