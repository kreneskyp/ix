import React, { useCallback, useMemo } from "react";
import { Box, FormLabel, Input, Textarea } from "@chakra-ui/react";
import { Editable, Slate, withReact } from "slate-react";
import { withHistory } from "slate-history";
import { createEditor } from "slate";
import { INITIAL_EDITOR_CONTENT } from "utils/slate";
import { NodeResizeControl, NodeResizer } from "reactflow";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const FunctionSchemaNode = ({ config, onFieldChange }) => {
  const editor = useMemo(() => withReact(withHistory(createEditor())), []);

  const { code } = useEditorColorMode();

  const handleChange = useCallback(
    (e) => {
      onFieldChange(e.target.name, e.target.value);
    },
    [onFieldChange]
  );

  return (
    <>
      <Box p={2} minWidth={200}>
        <FormLabel justify="start">Name</FormLabel>
        <Input name="name" value={config.name} onChange={handleChange} />
        <FormLabel justify="start">Description</FormLabel>
        <Textarea
          name="description"
          value={config.description}
          onChange={handleChange}
        ></Textarea>
        <FormLabel justify="start">Parameters</FormLabel>
        <Textarea
          name="parameters"
          value={config.parameters}
          onChange={handleChange}
          color={code.color}
          bg={code.bg}
          fontFamily="monospace"
          font="monospace"
          fontSize="sm"
        ></Textarea>
      </Box>
      <NodeResizeControl
        variant={"line"}
        minWidth={250}
        style={{ border: 0 }}
      />
    </>
  );
};
