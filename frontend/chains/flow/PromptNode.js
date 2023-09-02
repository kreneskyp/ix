import React from "react";
import PromptEditor from "chains/editor/PromptEditor";

export const PromptNode = ({ node, onChange }) => {
  return (
    <PromptEditor key={node.id} data={node.config} onChange={onChange.config} />
  );
};
