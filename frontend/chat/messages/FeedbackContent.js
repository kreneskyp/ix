import React from "react";
import { Flex } from "@chakra-ui/react";
import HighlightText from "components/HighlightText";

const FeedbackContent = ({ content }) => {
  return (
    <Flex direction="column" mt="4">
      <HighlightText content={content.feedback} />
    </Flex>
  );
};

export default FeedbackContent;
