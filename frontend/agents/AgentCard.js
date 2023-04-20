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

  if (agent == null) {
    return null;
  }

  return (
    <Card overflow="hidden" boxShadow="sm" width="100%" cursor="pointer">
      <CardBody>
        <VStack alignItems="start" spacing={2}>
          <Heading as="h5" size="xs">
            {agent.name}
          </Heading>
          <Text as="h5" size="xs">
            <strong>Model:</strong> {agent.model}
          </Text>

          <Box
            maxWidth="350px"
            height={75}
            overflow="hidden"
            textOverflow="ellipsis"
            css={{
              display: "-webkit-box",
              WebkitBoxOrient: "vertical",
              WebkitLineClamp: 3,
            }}
          >
            <strong>Purpose:</strong> {agent.purpose}
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default AgentCard;
