import React from "react";
import PropTypes from "prop-types";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Text } from "@chakra-ui/react";

const Avatar = ({ icon, size, color }) => {
  return (
    <Text as="span" color={color}>
      <FontAwesomeIcon icon={icon} size={size} color={color} />
    </Text>
  );
};

Avatar.propTypes = {
  icon: PropTypes.oneOfType([PropTypes.object, PropTypes.string]).isRequired,
  size: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
};

export default Avatar;
