import React from "react";
import { HStack, VStack, Text, Box, useColorModeValue } from "@chakra-ui/react";
import AssistantAvatar from "chat/avatars/AssistantAvatar";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSquareMinus } from "@fortawesome/free-solid-svg-icons";
import RemoveAgentModalTrigger from "chat/agents/RemoveAgentModalTrigger";
import { useColorMode } from "@chakra-ui/color-mode";

const AgentListItem = ({ chat, agent, onUpdateAgents }) => {
  const avatarColor = useColorModeValue("blue.400", "blue.300");

  return (
    <Box bg="transparent" width="100%">
      <HStack whiteSpace="nowrap">
        <AssistantAvatar agent={agent} color={avatarColor} />{" "}
        <Text>{agent.name}</Text>
        <Box
          width="100%"
          align="right"
          color="transparent"
          _hover={{
            color: "whiteAlpha.400",
          }}
        >
          {agent.id === chat.lead_id ? null : (
            <RemoveAgentModalTrigger
              chat={chat}
              agent={agent}
              onSuccess={onUpdateAgents}
            >
              <FontAwesomeIcon icon={faSquareMinus} />
            </RemoveAgentModalTrigger>
          )}
        </Box>
      </HStack>
    </Box>
  );
};

const SideBarAgentList = ({ graph, onUpdateAgents, agentPage }) => {
  const { colorMode } = useColorMode();
  const lead = graph.lead;
  const agents = agentPage?.objects;

  return (
    <Box
      justify="left"
      px={3}
      pb={3}
      pt={1}
      border="0px solid"
      borderRadius={5}
      borderColor={colorMode === "light" ? "gray.300" : "gray.600"}
      bg={colorMode === "light" ? "transparent" : "transparent"}
      color={colorMode === "light" ? "gray.800" : "gray.300"}
    >
      <VStack spacing={3}>
        <AgentListItem agent={lead} chat={graph.chat} />
        {agents?.map((agent, i) => (
          <AgentListItem
            key={i}
            chat={graph.chat}
            agent={agent}
            onUpdateAgents={onUpdateAgents}
          />
        ))}
      </VStack>
    </Box>
  );
};

export default SideBarAgentList;
