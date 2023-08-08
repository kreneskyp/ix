import React, { useCallback } from "react";
import { HStack, VStack, Text, Box, useColorModeValue } from "@chakra-ui/react";
import AssistantAvatar from "chat/AssistantAvatar";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSquareMinus, faUserPlus } from "@fortawesome/free-solid-svg-icons";
import RemoveAgentModalTrigger from "chat/agents/RemoveAgentModalTrigger";
import AddAgentModalTrigger from "chat/agents/AddAgentModalTrigger";
import { useColorMode } from "@chakra-ui/color-mode";

const AgentListItem = ({ chat, agent, onUpdateAgents }) => {
  const avatarColor = useColorModeValue("gray.700", "gray.400");

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
const SideBarAgentList = ({ graph, loadGraph }) => {
  const { colorMode } = useColorMode();
  const lead = graph.lead;
  const agents = graph.agents;
  const onUpdateAgents = useCallback(() => {
    loadGraph();
  }, [loadGraph]);

  return (
    <Box
      justify="left"
      px={3}
      pb={3}
      pt={1}
      border="1px solid"
      borderRadius={5}
      borderColor={colorMode === "light" ? "gray.400" : "gray.700"}
      bg={colorMode === "light" ? "gray.300" : "gray.800"}
      color={colorMode === "light" ? "gray.800" : "gray.300"}
    >
      <HStack
        width="100%"
        mb={2}
        color={colorMode === "light" ? "gray.800" : "whiteAlpha.500"}
      >
        <Text fontSize="xs" fontWeight="bold" mb={2}>
          Agents
        </Text>
        <Box width="100%" align="right">
          <AddAgentModalTrigger graph={graph} onSuccess={onUpdateAgents}>
            <FontAwesomeIcon icon={faUserPlus} />
          </AddAgentModalTrigger>
        </Box>
      </HStack>
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
