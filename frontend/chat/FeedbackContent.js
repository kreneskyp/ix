import React from "react";
import { Flex, Text } from "@chakra-ui/react";

const UserFeedback = ({ content }) => {
  return (
    <Flex direction="column" mt="4">
      {content.feedback && <Text mb="2">{content.feedback}</Text>}
    </Flex>
  );
};

export default UserFeedback;
