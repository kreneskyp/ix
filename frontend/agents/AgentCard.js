import React from "react";
import {
  Box,
  Card,
  CardBody,
  Heading,
  Text,
  useDisclosure,
  VStack,
} from "@chakra-ui/react";
import { useAgent } from "agents/graphql/AgentProvider";
import { AgentDetailModal } from "agents/AgentDetailModal";

const AgentCard = () => {
  const { agent } = useAgent();
  const { isOpen, onOpen, onClose } = useDisclosure();

  if (agent == null) {
    return null;
  }

  return (
    <>
      <AgentDetailModal agent={agent} isOpen={isOpen} onClose={onClose} />
      <Card
        onClick={onOpen}
        overflow="hidden"
        boxShadow="sm"
        width="100%"
        cursor="pointer"
      >
        <CardBody>
          <VStack alignItems="start" spacing={2}>
            <Heading as="h5" size="xs">
              {agent.name}
            </Heading>
            <Text as="h5" size="xs">
              <strong>Model:</strong> {agent.model}
            </Text>
            <Text as="h6" size="xs">
              <strong>Purpose:</strong> {agent.purpose}
            </Text>
          </VStack>
        </CardBody>
      </Card>
    </>
  );
};

export default AgentCard;
