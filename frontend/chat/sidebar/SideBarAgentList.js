import React from "react";
import { HStack, VStack, Text, Box } from "@chakra-ui/react";
import { usePreloadedQuery } from "react-relay/hooks";
import { ChatByIdQuery } from "chat/graphql/ChatByIdQuery";
import AssistantAvatar from "chat/AssistantAvatar";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSquareMinus, faUserPlus } from "@fortawesome/free-solid-svg-icons";
import RemoveAgentModalTrigger from "chat/agents/RemoveAgentModalTrigger";
import AddAgentModalTrigger from "chat/agents/AddAgentModalTrigger";

const AgentListItem = ({ chat, agent }) => {
  return (
    <Box bg="transparent" width="100%">
      <HStack whiteSpace="nowrap">
        <AssistantAvatar agent={agent} /> <Text>{agent.name}</Text>
        <Box
          width="100%"
          align="right"
          color="transparent"
          _hover={{
            color: "whiteAlpha.400",
          }}
        >
          {agent.id === chat.lead.id ? null : (
            <RemoveAgentModalTrigger chat={chat} agent={agent}>
              <FontAwesomeIcon icon={faSquareMinus} />
            </RemoveAgentModalTrigger>
          )}
        </Box>
      </HStack>
    </Box>
  );
};
const SideBarAgentList = ({ queryRef }) => {
  const { chat } = usePreloadedQuery(ChatByIdQuery, queryRef);
  const lead = chat.lead;
  const agents = chat.agents;

  return (
    <Box
      justify="left"
      px={3}
      pb={3}
      pt={1}
      borderRadius={5}
      bg="gray.800"
      color="gray.300"
    >
      <HStack width="100%" mb={2}>
        <Text fontSize="xs" color="whiteAlpha.500" fontWeight="bold" mb={2}>
          Agents
        </Text>
        <Box width="100%" align="right" color="whiteAlpha.500">
          <AddAgentModalTrigger chat={chat}>
            <FontAwesomeIcon icon={faUserPlus} />
          </AddAgentModalTrigger>
        </Box>
      </HStack>
      <VStack spacing={3}>
        <AgentListItem agent={lead} chat={chat} />
        {agents?.map((agent, i) => (
          <AgentListItem key={i} chat={chat} agent={agent} />
        ))}
      </VStack>
    </Box>
  );
};

export default SideBarAgentList;
