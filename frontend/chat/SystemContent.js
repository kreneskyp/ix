import React from "react";
import { Text } from "@chakra-ui/react";
import PropTypes from "prop-types";

const SystemContent = ({ content }) => {
  return <Text mt="4">{content.message}</Text>;
};

SystemContent.propTypes = {
  content: PropTypes.string.isRequired,
};

export default SystemContent;
