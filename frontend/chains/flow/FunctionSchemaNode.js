import React, { useCallback, useMemo } from "react";
import { Box, FormLabel, Input, Textarea } from "@chakra-ui/react";
import { Editable, Slate, withReact } from "slate-react";
import { withHistory } from "slate-history";
import { createEditor } from "slate";
import { INITIAL_EDITOR_CONTENT } from "utils/slate";
import { NodeResizeControl, NodeResizer } from "reactflow";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { SCROLLBAR_CSS } from "site/css";

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
        <NodeResizeControl
          variant={"line"}
          minWidth={250}
          position={"left"}
          h={"100%"}
          w={"10px"}
          style={{ border: "5px solid transparent" }}
        />
        <FormLabel justify="start">Name</FormLabel>
        <Input name="name" value={config.name} onChange={handleChange} />
        <FormLabel justify="start">Description</FormLabel>
        <Textarea
          name="description"
          value={config.description}
          onChange={handleChange}
          css={SCROLLBAR_CSS}
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
          css={SCROLLBAR_CSS}
        />
        <NodeResizeControl
          variant={"line"}
          minWidth={250}
          h={"100%"}
          style={{ border: "5px solid transparent" }}
        />
      </Box>
    </>
  );
};
