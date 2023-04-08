import React from "react";
import { VStack, Text } from "@chakra-ui/react";
import { TasksProvider } from "tasks/contexts";
import TasksTable from "tasks/TasksTable";

export const TasksListView = () => {
  return (
    <TasksProvider>
      <VStack>
        <TasksTable />
      </VStack>
    </TasksProvider>
  );
};
