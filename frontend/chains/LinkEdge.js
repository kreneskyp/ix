import React from "react";
import { BaseEdge } from "chains/BaseEdge";

export const LinkEdge = (props) => {
  const { targetX, targetY, style } = props;

  // Calculate the position for translating the marker
  // You might want to adjust these offsets to position the marker correctly relative to the target node
  const markerOffsetX = targetX;
  const markerOffsetY = targetY;

  // Apply scaling in addition to the translation
  const transform = `translate(${markerOffsetX}, ${markerOffsetY}) scale(1.3)`;

  return (
    <BaseEdge
      {...props}
      endMarker={
        <g transform={transform} style={style} fill={style.stroke}>
          <polyline
            points="-5,-4 0,0 -5,4 -5,-4"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1}
          />
        </g>
      }
    />
  );
};
