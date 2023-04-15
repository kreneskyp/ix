import React from "react";
import { Text } from "@chakra-ui/react";
import PropTypes from "prop-types";

const AuthRequestContent = ({ content }) => {
  return (
    <Text mt="4">
      Requesting authorization for message_id={content.messageId}
    </Text>
  );
};

AuthRequestContent.propTypes = {
  content: PropTypes.object.isRequired,
};

export default AuthRequestContent;
