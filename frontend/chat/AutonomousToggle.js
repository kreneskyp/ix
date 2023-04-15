import React from "react";
import { Box, Flex, Switch, Text, useToast } from "@chakra-ui/react";
import useSetTaskAutonomous from "tasks/graphql/useSetTaskAutonomous";
import { useTask } from "tasks/contexts";

export const TaskToggle = () => {
  const { task, refresh: refreshTask } = useTask();
  const { setTaskAutonomous } = useSetTaskAutonomous();
  const toast = useToast();
  const handleToggle = async () => {
    try {
      await setTaskAutonomous(task.id, !task.autonomous);
      refreshTask();
    } catch (error) {
      toast({
        title: "Error updating task",
        description:
          error.message || "An error occurred while updating the task.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Flex alignItems="center">
      <Text fontSize="md" fontWeight="medium" marginRight="2">
        Autonomous
      </Text>
      <Box>
        <Switch
          size="md"
          isChecked={task.autonomous}
          onChange={handleToggle}
          colorScheme="blue"
        />
      </Box>
    </Flex>
  );
};

export default TaskToggle;
