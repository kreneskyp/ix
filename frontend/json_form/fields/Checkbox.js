import React from "react";
import {
  Checkbox as ChakraCheckbox,
  FormLabel,
  HStack,
} from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { getLabel } from "json_form/utils";

export const Checkbox = ({ name, field, value, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = React.useCallback(
    (event) => {
      onChange(name, event.target.checked);
    },
    [field, onChange]
  );

  return (
    <HStack width="100%">
      <FormLabel justify="start">{getLabel(name)}</FormLabel>
      <ChakraCheckbox
        isChecked={value}
        onChange={handleChange}
        {...colorMode.input}
      />
    </HStack>
  );
};
