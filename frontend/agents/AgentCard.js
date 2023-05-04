import React from "react";
import {
  Box,
  Card,
  CardBody,
  Divider,
  Heading,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useAgent } from "agents/graphql/AgentProvider";

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
            {agent.model}
          </Text>
          <Divider />
          <Heading as="h5" size="xs">
            {agent.chain.name}
          </Heading>
          <Box
            maxWidth="350px"
            minHeight={50}
            maxHeight={75}
            overflow="hidden"
            textOverflow="ellipsis"
            css={{
              display: "-webkit-box",
              WebkitBoxOrient: "vertical",
              WebkitLineClamp: 3,
            }}
          >
            {agent.chain.description}
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default AgentCard;
