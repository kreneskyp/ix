import React from "react";
import {Flex, Heading, Text} from "@chakra-ui/react";

const ExecuteErrorContent = ({ content }) => {
    let relatedMsg;
    if (content.relatedMessageId !== null) {
        relatedMsg = (
            <Text mb={5}>
        Error executing command message_id={content.relatedMessageId}.
      </Text>
        );
    }

  return (
    <Flex direction="column" mt="4" color="red.300">
        <Heading size="sm">{content.errorType}</Heading>
        {relatedMsg}
      <Text mb={5}>{content.text}</Text>
    </Flex>
  );
};

export default ExecuteErrorContent;
