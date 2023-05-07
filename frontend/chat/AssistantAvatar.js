import React from "react";
import PropTypes from "prop-types";
import { library } from "@fortawesome/fontawesome-svg-core";
import Avatar from "./Avatar";
import { faMap, faRobot } from "@fortawesome/free-solid-svg-icons";

library.add(faRobot, faMap);

const AssistantAvatar = ({ agent, size, color }) => {
  // Check if agent.icon is a valid icon and render it, else render the default 'robot' icon
  const iconName = agent?.icon || "robot";

  const state = {
    icon: iconName,
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
  size: "lg",
  color: "gray.300",
};

export default AssistantAvatar;
