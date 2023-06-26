import React from "react";
import PromptEditor from "chains/editor/PromptEditor";
import { Box } from "@chakra-ui/react";

export const PromptNode = ({ config, onChange }) => {
  return (
    <Box p={2}>
      <PromptEditor data={config} onChange={onChange} />
    </Box>
  );
};
