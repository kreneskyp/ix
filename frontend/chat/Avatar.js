import React from "react";
import PropTypes from "prop-types";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const Avatar = ({ icon, size, color }) => {
  return <FontAwesomeIcon icon={icon} size={size} color={color} />;
};

Avatar.propTypes = {
  icon: PropTypes.oneOfType([PropTypes.object, PropTypes.string]).isRequired,
  size: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
};

export default Avatar;
