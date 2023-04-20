import React from "react";
import { Box, Flex } from "@chakra-ui/react";
import AgentCard from "agents/AgentCard";
import { AgentProvider } from "agents/graphql/AgentProvider";
import { AgentsQuery } from "agents/graphql/AgentsQuery";
import { usePreloadedQuery } from "react-relay/hooks";
import { Link } from "react-router-dom";

export const AgentCardList = ({ queryRef }) => {
  const { agents } = usePreloadedQuery(AgentsQuery, queryRef);
  return (
    <Flex align="center" justify="left" flexWrap="wrap">
      {agents.map((agent) => (
        <Box key={agent.id} p={5} width="400px">
          <AgentProvider agentId={agent.id}>
            <Link to={`/agents/${agent.id}`}>
              <AgentCard />
            </Link>
          </AgentProvider>
        </Box>
      ))}
    </Flex>
  );
};
