import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

export const StyledIcon = ({ style }) => {
  let iconProps = {};
  let IconComponent = FontAwesomeIcon;
  if (style.icon !== undefined) {
    iconProps.icon = style;
  } else if (style.props !== undefined) {
    iconProps = style.props;
  } else if (style.component !== undefined) {
    IconComponent = style.component;
  }
  return <IconComponent {...iconProps} />;
};
