import React from "react";
import { BaseEdge } from "chains/BaseEdge";

export const PropEdge = (props) => {
  const circlePosition = {
    cx: props.targetX,
    cy: props.targetY,
  };
  return (
    <BaseEdge
      {...props}
      endMarker={
        <circle
          cx={circlePosition.cx - 3}
          cy={circlePosition.cy}
          r={4.8} // Radius of the circle
          fill={props.style.stroke}
        />
      }
    />
  );
};
