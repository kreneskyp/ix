import React from "react";

import { FormControl, FormErrorMessage, FormLabel } from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";
import CodeEditor from "components/code_editor/CodeEditor";

export const JSONSchemaFormRightPanel = ({ schema, onChange }) => {
  const [state, setState] = React.useState({});
  const [value, setValue] = React.useState(
    JSON.stringify(schema?.value, null, 2)
  );

  const handleChange = React.useCallback(
    (newValue) => {
      setValue(newValue);

      let as_object;
      try {
        as_object = JSON.parse(newValue);
      } catch (e) {
        setState({ error: e.message });
        return;
      }
      setState({});
      onChange({ value: as_object });
    },
    [onChange]
  );

  return (
    <FormControl name="value" isInvalid={state?.error !== undefined}>
      <FormLabel justify="start">Schema</FormLabel>
      <CodeEditor value={value} language="json" onChange={handleChange} />
      <FormErrorMessage>{state?.error}</FormErrorMessage>
    </FormControl>
  );
};
