import React from "react";
import { Flex, Text } from "@chakra-ui/react";

const FeedbackContent = ({ content }) => {
  return (
    <Flex direction="column" mt="4">
      <Text mb="2">{content.feedback}</Text>
    </Flex>
  );
};

export default FeedbackContent;
