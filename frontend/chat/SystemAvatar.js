import React from "react";
import PropTypes from "prop-types";
import { faCog } from "@fortawesome/free-solid-svg-icons";
import Avatar from "./Avatar";

const SystemAvatar = ({ size, color }) => {
  const state = {
    icon: faCog,
    size: size,
    color: color,
  };

  return <Avatar {...state} />;
};

SystemAvatar.propTypes = {
  size: PropTypes.string,
  color: PropTypes.string,
};

SystemAvatar.defaultProps = {
  size: "2x",
  color: "gray",
};

export default SystemAvatar;
