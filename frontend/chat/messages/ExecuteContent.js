import React from "react";
import { Flex, Text } from "@chakra-ui/react";

const ExecuteContent = ({ message }) => {
  return (
    <Flex direction="column" mt="4">
      <Text>{message.content.output}</Text>
    </Flex>
  );
};

export default ExecuteContent;
