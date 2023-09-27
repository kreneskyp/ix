import React from "react";
import {
  Box,
  Card,
  CardBody,
  Flex,
  Heading,
  HStack,
  Switch,
  Text,
  VStack,
} from "@chakra-ui/react";
import AssistantAvatar from "chat/avatars/AssistantAvatar";
import { useColorMode } from "@chakra-ui/color-mode";

export const AddAgentCard = ({ inChat, isLead, agent, ...props }) => {
  const { colorMode } = useColorMode();
  if (agent == null) {
    return null;
  }

  let sx = {
    border: "1px solid transparent",
    borderColor: colorMode === "light" ? "gray.300" : "transparent",
  };
  if (inChat || isLead) {
    sx = {
      border: "1px solid",
      borderColor: "blue.500",
    };
  }

  return (
    <Card
      overflow="hidden"
      boxShadow="sm"
      width={360}
      cursor="pointer"
      bg={colorMode === "light" ? "gray.200" : "blackAlpha.500"}
      sx={sx}
      {...props}
    >
      <CardBody p={5}>
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
            <VStack alignItems="start" spacing={2}>
              <Flex width={"100%"} justifyContent={"space-between"}>
                <Heading as="h5" size="xs">
                  {agent.name}
                </Heading>
                <Switch
                  size={"sm"}
                  isChecked={inChat || isLead}
                  isDisabled={isLead}
                  colorScheme={"blue"}
                />
              </Flex>
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
            </VStack>
          </Box>
        </HStack>
      </CardBody>
    </Card>
  );
};
