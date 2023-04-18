import React from "react";
import { Flex, Text } from "@chakra-ui/react";

const ExecuteContent = ({ content }) => {
  return (
    <Flex direction="column" mt="4">
      <Text mb="2">Executed command message_id={content.messageId}.</Text>
      <Text>{content.output}</Text>
    </Flex>
  );
};

export default ExecuteContent;
