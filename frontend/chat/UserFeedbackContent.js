import React from "react";
import { Flex, Text } from "@chakra-ui/react";

const UserFeedback = ({ content }) => {
  return (
    <Flex direction="column" mt="4">
      {content.authorized && content.authorized > 0 && (
        <Text mb="2">You have authorized {content.authorized} commands.</Text>
      )}
      {content.feedback && <Text mb="2">{content.feedback}</Text>}
    </Flex>
  );
};

export default UserFeedback;
