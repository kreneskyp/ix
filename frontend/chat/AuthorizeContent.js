import React from "react";
import { Flex, Text } from "@chakra-ui/react";

const AuthorizeContent = ({ content }) => {
  return (
    <Flex direction="column" mt="4">
      <Text mb="2">Authorizing command message_id={content.messageId}.</Text>
    </Flex>
  );
};

export default AuthorizeContent;
