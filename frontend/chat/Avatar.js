import React from "react";
import PropTypes from "prop-types";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const Avatar = ({ icon, size, color }) => {
  return (
    <div className="avatar">
      <FontAwesomeIcon icon={icon} size={size} color={color} />
    </div>
  );
};

Avatar.propTypes = {
  icon: PropTypes.object.isRequired,
  size: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
};

export default Avatar;
