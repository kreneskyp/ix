import React from "react";
import { HStack, VStack, Text, Box } from "@chakra-ui/react";
import { usePreloadedQuery } from "react-relay/hooks";
import { ChatByIdQuery } from "chat/graphql/ChatByIdQuery";
import AssistantAvatar from "chat/AssistantAvatar";
import AgentDetailModalButton from "agents/AgentDetailModalButton";

const AgentListItem = ({ agent }) => {
  return (
    <AgentDetailModalButton agent={agent} width="100%">
      <Box
        bg="transparent"
        _hover={{
          cursor: "pointer",
        }}
        width="100%"
      >
        <HStack>
          <AssistantAvatar agent={agent} /> <Text>{agent.name}</Text>
        </HStack>
      </Box>
    </AgentDetailModalButton>
  );
};
const SideBarAgentList = ({ queryRef }) => {
  const { chat } = usePreloadedQuery(ChatByIdQuery, queryRef);
  const lead = chat.lead;
  const agents = chat.agents;

  return (
    <Box justify="left" p={3} borderRadius={5} bg="gray.800" color="gray.300">
      <VStack spacing={3}>
        <AgentListItem agent={lead} />
        {agents?.map((agent, i) => (
          <AgentListItem key={i} agent={agent} />
        ))}
      </VStack>
    </Box>
  );
};

export default SideBarAgentList;
