import React from "react";
import {
  Card,
  CardBody,
  Heading,
  Text,
  HStack,
  VStack,
} from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { ChainEditButton } from "chains/ChainEditButton";
import { ModalClose } from "components/Modal";

const ChainCard = ({ chain, children, ...props }) => {
  const close = React.useContext(ModalClose);
  const { colorMode } = useColorMode();

  if (chain == null) {
    return null;
  }

  let sx = {
    border: "1px solid transparent",
    borderColor: colorMode === "light" ? "gray.300" : "transparent",
  };

  return (
    <Card
      overflow="hidden"
      boxShadow="sm"
      width={360}
      bg={colorMode === "light" ? "gray.200" : "blackAlpha.500"}
      sx={sx}
      {...props}
    >
      <CardBody px={5} pt={5} pb={2}>
        <VStack alignItems="start" spacing={2}>
          <Heading as="h5" size="xs">
            {chain.name}
          </Heading>
          <Text
            maxWidth="350px"
            minHeight={50}
            maxHeight={75}
            fontSize="sm"
            overflow="hidden"
            textOverflow="ellipsis"
            css={{
              display: "-webkit-box",
              WebkitBoxOrient: "vertical",
              WebkitLineClamp: 3,
            }}
          >
            {chain.description}
          </Text>
        </VStack>
        <HStack spacing={2} pt={4} display="flex" justifyContent="flex-end">
          <ChainEditButton chain={chain} onClick={close} />
        </HStack>
      </CardBody>
    </Card>
  );
};

export default ChainCard;
