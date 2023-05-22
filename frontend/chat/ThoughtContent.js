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
    </>
  );
};

ThoughtContent.propTypes = {
  content: PropTypes.object.isRequired,
};

export default ThoughtContent;
