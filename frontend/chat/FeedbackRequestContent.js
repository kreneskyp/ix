import React from "react";
import { Text } from "@chakra-ui/react";
import PropTypes from "prop-types";

const SystemFeedback = ({ content }) => {
  return <Text mt="4">{content.message}</Text>;
};

SystemFeedback.propTypes = {
  content: PropTypes.string.isRequired,
};

export default SystemFeedback;
