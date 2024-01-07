import React, { useCallback, useMemo } from "react";
import { FormLabel } from "@chakra-ui/react";
import { withReact } from "slate-react";
import { withHistory } from "slate-history";
import { createEditor } from "slate";
import { useEditorColorMode } from "chains/editor/useColorMode";
import AutoResizingTextarea from "components/AutoResizingTextArea";

export const FunctionSchemaNode = ({ node, onChange }) => {
  const editor = useMemo(() => withReact(withHistory(createEditor())), []);

  const { code, scrollbar } = useEditorColorMode();

  const handleChange = useCallback(
    (e) => {
      onChange.field(e.target.name, e.target.value);
    },
    [onChange]
  );

  return (
    <>
      <FormLabel justify="start">Parameters</FormLabel>
      <AutoResizingTextarea
        name="parameters"
        value={node.config.parameters}
        onChange={handleChange}
        color={code.color}
        bg={code.bg}
        fontFamily="monospace"
        font="monospace"
        fontSize="sm"
        css={scrollbar}
        placeholder={"Enter JSON Schema for function parameters."}
      />
    </>
  );
};
