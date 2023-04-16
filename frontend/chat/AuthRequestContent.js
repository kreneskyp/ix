import React from "react";
import { Box, Flex, Text } from "@chakra-ui/react";
import PropTypes from "prop-types";
import AuthorizeCommandButton from "chat/AuthorizeCommandButton";

const AuthRequestContent = ({ content }) => {
  return (
    <Box>
      <Text mb="4">
        Requesting authorization for message_id={content.messageId}
      </Text>
      <Flex justifyContent="flex-end">
        <AuthorizeCommandButton messageId={content.messageId} />
      </Flex>
    </Box>
  );
};

AuthRequestContent.propTypes = {
  content: PropTypes.object.isRequired,
};

export default AuthRequestContent;
