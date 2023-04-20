import React from "react";
import { Flex, Heading, Text } from "@chakra-ui/react";

const ExecuteErrorContent = ({ content }) => {
  let relatedMsg;
  if (content.message_id !== null) {
    relatedMsg = (
      <Text mb={5}>
        Error executing command message_id={content.message_id}.
      </Text>
    );
  }

  return (
    <Flex direction="column" mt="4" color="red.300">
      <Heading size="sm">{content.error_type}</Heading>
      {relatedMsg}
      <Text mb={5}>{content.text}</Text>
    </Flex>
  );
};

export default ExecuteErrorContent;
