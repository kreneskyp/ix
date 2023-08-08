import React from "react";
import { Box, Flex } from "@chakra-ui/react";
import { Link } from "react-router-dom";
import ChainCard from "chains/ChainCard";

export const ChainCardList = ({ page = {} }) => {
  const { objects: chains } = page;

  return (
    <Flex align="center" justify="left" flexWrap="wrap">
      {chains?.map((chain) => (
        <Box key={chain.id} p={5} width="400px">
          <Link to={`/chains/${chain.id}`}>
            <ChainCard chain={chain} />
          </Link>
        </Box>
      ))}
    </Flex>
  );
};
