import React from "react";
import { HStack, VStack, Text, Box } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSquare, faSquareCheck } from "@fortawesome/free-regular-svg-icons";
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
            <Text color="whitesmoke" fontSize="sm">
              <FontAwesomeIcon
                icon={goal.complete ? faSquareCheck : faSquare}
                marginRight={5}
              />
              <span style={{ marginLeft: 5 }}>{goal.description}</span>
            </Text>
          </VStack>
        ))}
      </VStack>
    </Box>
  );
};

export default SideBarGoalList;
