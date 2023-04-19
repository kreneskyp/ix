import React from "react";
import { Box, Flex } from "@chakra-ui/react";
import AgentCard from "agents/AgentCard";
import { AgentProvider } from "agents/graphql/AgentProvider";
import { AgentsQuery } from "agents/graphql/AgentsQuery";
import { usePreloadedQuery } from "react-relay/hooks";

export const AgentCardList = ({ queryRef }) => {
  const { agents } = usePreloadedQuery(AgentsQuery, queryRef);
  console.log(agents);
  return (
    <Flex align="center" justify="left" flexWrap="wrap">
      {agents.map((agent) => (
        <Box key={agent.id} p={5} width="400px">
          <AgentProvider agentId={agent.id}>
            <AgentCard />
          </AgentProvider>
        </Box>
      ))}
    </Flex>
  );
};
