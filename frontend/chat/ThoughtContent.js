import React from "react";
import { Text, useColorModeValue } from "@chakra-ui/react";
import PropTypes from "prop-types";

const ThoughtContent = ({ content }) => {
  const textColor = useColorModeValue("gray.600", "gray.400");

  return (
    <>
      <Text mt="4" color={textColor}>
        <b>Runtime:</b> {content.runtime.toFixed(2)} seconds.
      </Text>
      <Text mt="4" color={textColor}>
        <b>Prompt Tokens:</b> {content.usage?.prompt_tokens}
      </Text>
      <Text mt="4" color={textColor}>
        <b>Completion Tokens:</b> {content.usage?.completion_tokens}
      </Text>
      <Text mt="4" color={textColor}>
        <b>Total Tokens:</b> {content.usage?.total_tokens}
      </Text>
    </>
  );
};

ThoughtContent.propTypes = {
  content: PropTypes.object.isRequired,
};

export default ThoughtContent;
