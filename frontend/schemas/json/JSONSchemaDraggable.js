import React from "react";
import { DraggableNode } from "chains/editor/DraggableNode";
import { ListItemNode } from "components/ListItemNode";

const DRAGGABLE_CONFIG = {
  class_path: "ix.runnable.schema.LoadSchema",
  label: "Load Schema",
};

export const JSONSchemaDraggable = ({ schema }) => {
  return (
    <DraggableNode
      {...DRAGGABLE_CONFIG}
      name={`Load: ${schema.name}`}
      description={schema.description}
      config={{ schema_id: schema.id }}
      height={"100%"}
    >
      <ListItemNode label={"Load Schema"} />
    </DraggableNode>
  );
};
