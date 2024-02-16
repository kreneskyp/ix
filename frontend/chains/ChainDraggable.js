import React from "react";
import { DraggableButton } from "chains/DraggableButton";

export const ChainDraggable = ({ chain }) => {
  return (
    <DraggableButton
      name={chain.name}
      description={chain.description}
      config={{ chain_id: chain.id }}
      class_path="ix.runnable.flow.load_chain_id"
      label="Reference"
      highlight={"blue.400"}
    />
  );
};
