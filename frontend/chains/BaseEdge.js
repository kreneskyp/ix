import React from "react";
import { getSmoothStepPath, EdgeText } from "reactflow";
import { getLoopPath } from "chains/edges";

// use getSmoothStepPath when target is to the right of source
export const useEdgePath = (
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition
) => {
  const get_path =
    sourceX + 30 < targetX || targetY > sourceY + 160
      ? getSmoothStepPath
      : getLoopPath;
  const [edgePath] = get_path({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });
  return edgePath;
};

export const BaseEdge = ({
  id,
  path,
  labelX,
  labelY,
  label,
  labelStyle,
  labelShowBg,
  labelBgStyle,
  labelBgPadding,
  labelBgBorderRadius,
  style,
  markerEnd,
  markerStart,
  interactionWidth = 20,
  sourceX,
  sourceY,
  sourcePosition,
  targetX,
  targetY,
  targetPosition,
  startMarker,
  endMarker,
}) => {
  const edgePath = useEdgePath(
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition
  );

  return (
    <>
      {startMarker}
      <path
        id={id}
        style={style}
        d={edgePath}
        className={"react-flow__edge-path"}
        fill="none"
        markerEnd={markerEnd}
        markerStart={markerStart}
      />
      {endMarker}
      {interactionWidth && (
        <path
          d={path}
          fill="none"
          strokeOpacity={0}
          strokeWidth={interactionWidth}
          className="react-flow__edge-interaction"
        />
      )}
      {label && isNumeric(labelX) && isNumeric(labelY) ? (
        <EdgeText
          x={labelX}
          y={labelY}
          label={label}
          labelStyle={labelStyle}
          labelShowBg={labelShowBg}
          labelBgStyle={labelBgStyle}
          labelBgPadding={labelBgPadding}
          labelBgBorderRadius={labelBgBorderRadius}
        />
      ) : null}
    </>
  );
};
