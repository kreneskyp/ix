import React from "react";
import {
  Box,
  Card,
  CardBody,
  Divider,
  Flex,
  Heading,
  Text,
  useColorModeValue,
  VStack,
} from "@chakra-ui/react";

const AgentCard = ({ agent }) => {
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
          <Flex justify={"space-between"} width={"100%"}>
            <Heading as="span" size="sm">
              {agent.name}
            </Heading>
            <Text fontSize="sm" color="blue.400">
              @{agent.alias}
            </Text>
          </Flex>

          <Divider />
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
            {agent.purpose}
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default AgentCard;
