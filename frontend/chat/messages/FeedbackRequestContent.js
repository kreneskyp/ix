import React from "react";
import { Text, useColorModeValue } from "@chakra-ui/react";
import PropTypes from "prop-types";

const FeedbackRequestContent = ({ content }) => {
  const labelColor = useColorModeValue("black", "blue.300");
  const textColor = useColorModeValue("gray.600", "gray.400");

  return (
    <>
      <Text mt="4" color={labelColor}>
        <b>I require input:</b>
      </Text>
      <Text mt="4" color={textColor}>
        {content.question}
      </Text>
    </>
  );
};

FeedbackRequestContent.propTypes = {
  content: PropTypes.object.isRequired,
};

export default FeedbackRequestContent;
