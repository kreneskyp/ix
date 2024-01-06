import React from "react";
import {
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath,
  Position,
} from "reactflow";

export default function ContainerEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  children,
  ...props
}) {
  const [path, labelX, labelY, offsetX, offsetY] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition: Position.Right,
    targetX,
    targetY,
    targetPosition: Position.Left,
  });

  return (
    <>
      <BaseEdge id={id} path={path} {...props} />
      <EdgeLabelRenderer>
        <div
          style={{
            position: "absolute",
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: "all",
            zIndex: 10,
          }}
          className="nodrag nopan"
        >
          {children}
        </div>
      </EdgeLabelRenderer>
    </>
  );
}
