import React from "react";
import { DraggableNode } from "chains/editor/DraggableNode";
import { ListItemNode } from "components/ListItemNode";

export const DRAGGABLE_CONFIG = {
  class_path: "ix.runnable.openapi.RunOpenAPIRequest",
  label: "Run OpenAPI Request",
};

export const OpenAPIDraggable = ({ schema }) => {
  // name and description for RunOpenAPIRequest should be taken from the action (path+method)
  // which aren't known here. Set the schema_id only.
  return (
    <DraggableNode
      {...DRAGGABLE_CONFIG}
      name=""
      description=""
      config={{ schema_id: schema.id }}
      height={"100%"}
    >
      <ListItemNode label={"OpenAPI Request"} expanded={150} />
    </DraggableNode>
  );
};
