import React from "react";
import {
  HStack,
  VStack,
  Text,
  Box,
  Card,
  CardHeader,
  CardBody,
  Heading,
  useDisclosure,
  Button,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSquare, faSquareCheck } from "@fortawesome/free-regular-svg-icons";
import { useTask } from "tasks/contexts";
import { AgentDetailModal } from "agents/AgentDetailModal";

const SideBarGoalList = () => {
  const { task } = useTask();

  return (
    <Card>
      <CardHeader mb={0} pb={0}>
        <Heading size="xs" textTransform="uppercase">
          Goals
        </Heading>
      </CardHeader>
      <CardBody>
        <VStack align="flex-start" spacing={2}>
          {task.goals?.map((goal, i) => (
            <VStack key={i} align="flex-start" spacing={0}>
              <Text fontSize="xs">
                <FontAwesomeIcon
                  icon={goal.complete ? faSquareCheck : faSquare}
                />
                <span style={{ marginLeft: 5 }}>{goal.description}</span>
              </Text>
            </VStack>
          ))}
        </VStack>
      </CardBody>
    </Card>
  );
};

export default SideBarGoalList;
