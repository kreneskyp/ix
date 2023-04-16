import React from "react";
import { Flex, Text } from "@chakra-ui/react";

const ExecuteErrorContent = ({ content }) => {
  return (
    <Flex direction="column" mt="4" color="red.300">
      <Text mb={5}>
        Error executing command message_id={content.messageId}.
      </Text>
      <Text mb={5}>{content.text}</Text>
    </Flex>
  );
};

export default ExecuteErrorContent;
