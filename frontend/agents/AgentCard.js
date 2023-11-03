import React from "react";
import { Box, Card, CardBody, HStack, Text, VStack } from "@chakra-ui/react";

import AssistantAvatar from "chat/avatars/AssistantAvatar";
import { useColorMode } from "@chakra-ui/color-mode";

export const AgentCard = ({ agent, children, ...props }) => {
  const { colorMode } = useColorMode();
  if (agent == null) {
    return null;
  }

  let sx = {
    border: "1px solid transparent",
    borderColor: colorMode === "light" ? "gray.300" : "transparent",
  };

  return (
    <Card
      overflow="hidden"
      boxShadow="sm"
      width={360}
      bg={colorMode === "light" ? "gray.200" : "blackAlpha.500"}
      sx={sx}
      {...props}
    >
      <CardBody px={5} pt={5} pb={2}>
        <HStack spacing={3}>
          <Box width={130}>
            <VStack justify="center" align="center">
              <AssistantAvatar agent={agent} />
              <Text
                color={colorMode === "light" ? "blue.500" : "blue.400"}
                fontSize="sm"
                fontWeight="bold"
              >
                @{agent.alias}
              </Text>
            </VStack>
          </Box>
          <Box width={400} sx={{ userSelect: "none" }}>
            <Text
              maxWidth="350px"
              minHeight={50}
              maxHeight={75}
              fontSize="sm"
              overflow="hidden"
              textOverflow="ellipsis"
              css={{
                display: "-webkit-box",
                WebkitBoxOrient: "vertical",
                WebkitLineClamp: 3,
              }}
            >
              {agent.purpose}
            </Text>
          </Box>
        </HStack>
        <HStack spacing={2} pt={4} display="flex" justifyContent="flex-end">
          {children}
        </HStack>
      </CardBody>
    </Card>
  );
};
