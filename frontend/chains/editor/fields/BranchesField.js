import React from "react";
import { useReactFlow } from "reactflow";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import { HashList } from "json_form/fields/HashList";

export const BranchesField = ({ ...props }) => {
  const reactFlowInstance = useReactFlow();
  const api = React.useContext(ChainEditorAPIContext);

  // if a row is deleted then the edge must be deleted from ReactFlow and API
  const handleDelete = React.useCallback(
    (hash, value) => {
      // sourceHandle is an uuid, so it is unique enough to find the edge
      const edge = reactFlowInstance
        .getEdges()
        .find((edge) => edge.sourceHandle === hash);
      if (edge !== undefined) {
        api.deleteEdge(edge.data.id);
        const updatedEdges = reactFlowInstance
          .getEdges()
          .filter((e) => e.id !== edge.id);
        reactFlowInstance.setEdges(updatedEdges);
      }
    },
    [reactFlowInstance, api]
  );

  return <HashList {...props} onDelete={handleDelete} />;
};
