import React from "react";
import { Text } from "@chakra-ui/react";
import PropTypes from "prop-types";

const SystemFeedbackRequestContent = ({ content }) => {
  return <Text mt="4">{content.question}</Text>;
};

SystemFeedbackRequestContent.propTypes = {
  content: PropTypes.object.isRequired,
};

export default SystemFeedbackRequestContent;
