import React from "react";
import {
  Box,
  Card,
  CardBody,
  Divider,
  Heading,
  Text,
  useColorModeValue,
  VStack,
} from "@chakra-ui/react";
import { useChain } from "chains/hooks/useChain";

const AgentCard = ({ agent }) => {
  const { data: chain } = useChain(agent?.chain_id);

  const borderColor = useColorModeValue("gray.400", "whiteAlpha.50");
  const bg = useColorModeValue("gray.100", "gray.700");

  if (agent == null) {
    return null;
  }

  return (
    <Card
      overflow="hidden"
      boxShadow="md"
      width="100%"
      cursor="pointer"
      border="1px solid"
      borderColor={borderColor}
      bg={bg}
    >
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
            {chain?.name || "No Chain"}
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
            {chain?.description || "No Chain"}
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default AgentCard;
