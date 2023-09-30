import React from "react";
import { Button, useToast } from "@chakra-ui/react";
import { useTask } from "tasks/contexts";
import useStartTask from "tasks/graphql/useStartTask";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlay } from "@fortawesome/free-solid-svg-icons";

export const TaskRunButton = () => {
  const { task } = useTask();
  const { startTask } = useStartTask();
  const toast = useToast();
  const handleStart = async () => {
    try {
      await startTask(task.id);
    } catch (error) {
      toast({
        title: "Error starting task",
        description:
          error.message || "An error occurred while starting the task.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Button onClick={handleStart} colorScheme="green" px={10}>
      Run
      <FontAwesomeIcon icon={faPlay} ml={5} style={{ paddingLeft: "5px" }} />
    </Button>
  );
};

export default TaskRunButton;
