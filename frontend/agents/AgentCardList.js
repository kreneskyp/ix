import React from "react";
import { Box, Flex } from "@chakra-ui/react";
import AgentCard from "agents/AgentCard";
import { Link } from "react-router-dom";

export const AgentCardList = ({ page = {} }) => {
  const { objects: agents } = page;
  return (
    <Flex align="center" justify="left" flexWrap="wrap">
      {agents?.map((agent) => (
        <Box key={agent.id} p={5} width="400px">
          <Link to={`/agents/${agent.id}`}>
            <AgentCard agent={agent} />
          </Link>
        </Box>
      ))}
    </Flex>
  );
};
