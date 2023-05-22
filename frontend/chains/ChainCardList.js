import React from "react";
import { Box, Flex } from "@chakra-ui/react";
import { ChainProvider } from "chains/graphql/ChainProvider";
import { ChainsQuery } from "chains/graphql/ChainsQuery";
import { usePreloadedQuery } from "react-relay/hooks";
import { Link } from "react-router-dom";
import ChainCard from "chains/ChainCard";

export const ChainCardList = ({ queryRef }) => {
  const { chains } = usePreloadedQuery(ChainsQuery, queryRef);
  return (
    <Flex align="center" justify="left" flexWrap="wrap">
      {chains.map((chain) => (
        <Box key={chain.id} p={5} width="400px">
          <ChainProvider chainId={chain.id}>
            <Link to={`/chains/${chain.id}`}>
              <ChainCard />
            </Link>
          </ChainProvider>
        </Box>
      ))}
    </Flex>
  );
};
