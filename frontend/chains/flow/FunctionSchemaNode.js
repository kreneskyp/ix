import React, { useCallback, useMemo } from "react";
import { Box, FormLabel, Input, Textarea } from "@chakra-ui/react";
import { Editable, Slate, withReact } from "slate-react";
import { withHistory } from "slate-history";
import { createEditor } from "slate";
import { INITIAL_EDITOR_CONTENT } from "utils/slate";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { SCROLLBAR_CSS } from "site/css";

export const FunctionSchemaNode = ({ node, onChange }) => {
  const editor = useMemo(() => withReact(withHistory(createEditor())), []);

  const { code } = useEditorColorMode();

  const handleChange = useCallback(
    (e) => {
      onChange.field(e.target.name, e.target.value);
    },
    [onChange]
  );

  return (
    <>
      <FormLabel justify="start">Parameters</FormLabel>
      <Textarea
        name="parameters"
        value={node.config.parameters}
        onChange={handleChange}
        color={code.color}
        bg={code.bg}
        fontFamily="monospace"
        font="monospace"
        fontSize="sm"
        css={SCROLLBAR_CSS}
        placeholder={"Enter JSON Schema for function parameters."}
      />
    </>
  );
};
