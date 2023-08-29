import React from "react";
import {
  Box,
  Card,
  CardBody,
  Heading,
  useColorModeValue,
  VStack,
} from "@chakra-ui/react";

const ChainCard = ({ chain }) => {
  if (chain == null) {
    return null;
  }

  const borderColor = useColorModeValue("gray.400", "whiteAlpha.50");
  const bg = useColorModeValue("gray.100", "gray.700");

  return (
    <Card
      overflow="hidden"
      boxShadow="sm"
      width="100%"
      cursor="pointer"
      border="1px solid"
      borderColor={borderColor}
      bg={bg}
    >
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
