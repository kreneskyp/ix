import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCode } from "@fortawesome/free-solid-svg-icons";

export const SkillIcon = ({ ...props }) => {
  return <FontAwesomeIcon icon={faCode} {...props} />;
};
