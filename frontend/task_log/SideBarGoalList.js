import React from "react";
import { VStack, Text, Box } from "@chakra-ui/react";
import { CheckIcon, CloseIcon } from "@chakra-ui/icons";
import { useTask } from "tasks/contexts";

const SideBarGoalList = () => {
  const { task } = useTask();

  return (
    <Box>
      <Text color="white" fontWeight="bold" mb={2}>
        Goals
      </Text>
      <VStack align="flex-start" spacing={2} px={5}>
        {task.goals?.map((goal, i) => (
          <VStack key={i} align="flex-start" spacing={0}>
            {goal.complete ? <CheckIcon mr={2} /> : <CloseIcon mr={2} />}
            <Text color="whitesmoke" fontSize="sm">
              {goal.description}
            </Text>
          </VStack>
        ))}
      </VStack>
    </Box>
  );
};

export default SideBarGoalList;
