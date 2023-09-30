import React from "react";
import PropTypes from "prop-types";
import { library } from "@fortawesome/fontawesome-svg-core";
import Avatar from "./Avatar";
import {
  faBrain,
  faMap,
  faRobot,
  faUserNinja,
  faUserSecret,
  faUserTie,
} from "@fortawesome/free-solid-svg-icons";

library.add(faRobot, faMap, faUserTie, faUserNinja, faUserSecret, faBrain);

const AssistantAvatar = ({ agent, size, color }) => {
  // Check if agent.icon is a valid icon and render it, else render the default 'robot' icon
  const iconName = agent?.icon || "brain";

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
