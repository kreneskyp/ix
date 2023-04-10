import React from "react";
import PropTypes from "prop-types";
import { faRobot } from "@fortawesome/free-solid-svg-icons";
import Avatar from "./Avatar";

const AssistantAvatar = ({ size, color }) => {
  const state = {
    icon: faRobot,
    size: size,
    color: color,
  };

  return <Avatar {...state} />;
};

AssistantAvatar.propTypes = {
  size: PropTypes.string,
  color: PropTypes.string,
};

AssistantAvatar.defaultProps = {
  size: "2x",
  color: "green",
};

export default AssistantAvatar;
