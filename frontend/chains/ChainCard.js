import React from "react";
import { Box, Card, CardBody, Heading, VStack } from "@chakra-ui/react";
import { useChain } from "chains/graphql/ChainProvider";

const ChainCard = () => {
  const { chain } = useChain();

  if (chain == null) {
    return null;
  }

  return (
    <Card overflow="hidden" boxShadow="sm" width="100%" cursor="pointer">
      <CardBody>
        <VStack alignItems="start" spacing={2}>
          <Heading as="h5" size="xs">
            {chain.name}
          </Heading>
          <Box
            maxWidth="350px"
            height={75}
            overflow="hidden"
            textOverflow="ellipsis"
            css={{
              display: "-webkit-box",
              WebkitBoxOrient: "vertical",
              WebkitLineClamp: 3,
            }}
          >
            {chain.description}
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default ChainCard;
