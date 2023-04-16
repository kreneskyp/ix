import React from "react";
import { Flex, Text } from "@chakra-ui/react";

const ExecuteError = ({ content }) => {
  return (
    <Flex direction="column" mt="4" color="red">
      <Text mb={5}>Error executing command message_id={content.messageId}.</Text>
        <Text mb={5}>{content.text}</Text>
    </Flex>
  );
};

export default ExecuteError;
