import React from "react";
import PropTypes from "prop-types";
import { faUser } from "@fortawesome/free-solid-svg-icons";
import Avatar from "./Avatar";

const UserAvatar = ({ size, color }) => {
  const state = {
    icon: faUser,
    size: size,
    color: color,
  };

  return <Avatar {...state} />;
};

UserAvatar.propTypes = {
  size: PropTypes.string,
  color: PropTypes.string,
};

UserAvatar.defaultProps = {
  size: "2x",
  color: "blue",
};

export default UserAvatar;
