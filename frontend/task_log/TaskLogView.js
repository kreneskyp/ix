import React from "react";
import { useParams } from "react-router-dom";
import { Grid, GridItem } from "@chakra-ui/react";

import TaskLogLeftPane from "task_log/TaskLogLeftPane";
import TaskLogCenterPane from "task_log/TaskLogCenterPane";
import { TaskProvider } from "tasks/contexts";

export const TaskLogView = () => {
  const { id } = useParams();

  return (
    <TaskProvider taskId={id}>
      <Grid
        h="calc(100vh)"
        templateRows="repeat(1)"
        templateColumns="repeat(5, 1fr)"
        gap={4}
      >
        <GridItem bg="blackAlpha.800">
          <TaskLogLeftPane />
        </GridItem>
        <GridItem colSpan={4}>
          <TaskLogCenterPane />
        </GridItem>
      </Grid>
    </TaskProvider>
  );
};

export default TaskLogView;
