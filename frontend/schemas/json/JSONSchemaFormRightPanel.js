import React from "react";

import {
  FormControl,
  FormErrorMessage,
  FormLabel,
  Textarea,
} from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const JSONSchemaFormRightPanel = ({ schema, onChange }) => {
  const [state, setState] = React.useState({});
  const { code, scrollbar, input } = useEditorColorMode();

  const [value, setValue] = React.useState();

  React.useEffect(() => {
    if (schema?.value) {
      // convert object to string
      const str = JSON.stringify(schema.value, null, 2);
      setValue(str);
    }
  }, []);

  const handleChange = React.useCallback(
    (e) => {
      setValue(e.target.value);

      let as_object;
      try {
        as_object = JSON.parse(e.target.value);
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
      <Textarea
        name="parameters"
        value={value}
        onChange={handleChange}
        color={code.color}
        bg={code.bg}
        fontFamily="monospace"
        font="monospace"
        fontSize="sm"
        {...input}
        css={scrollbar}
        placeholder={"Enter JSON Schema."}
        height={400}
        width={"100%"}
      />
      <FormErrorMessage>{state?.error}</FormErrorMessage>
    </FormControl>
  );
};
