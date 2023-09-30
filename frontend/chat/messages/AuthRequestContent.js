import React from "react";
import { Box, Flex, Text } from "@chakra-ui/react";
import PropTypes from "prop-types";
import AuthorizeCommandButton from "chat/buttons/AuthorizeCommandButton";

const AuthRequestContent = ({ content }) => {
  return (
    <Box>
      <Text mb="4">
        Requesting authorization for message_id={content.message_id}
      </Text>
      <Flex justifyContent="flex-end">
        <AuthorizeCommandButton messageId={content.message_id} />
      </Flex>
    </Box>
  );
};

AuthRequestContent.propTypes = {
  content: PropTypes.object.isRequired,
};

export default AuthRequestContent;
