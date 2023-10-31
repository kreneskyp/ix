import React from "react";
import { Input as ChakraInput, Flex, FormLabel } from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { getLabel } from "json_form/utils";

export const Secret = ({ name, field, isRequired, value, style, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = React.useCallback(
    (event) => {
      onChange({ [name]: event.target.value });
    },
    [field, onChange]
  );

  return (
    <Flex justifyContent="space-between" wrap="wrap" width="100%">
      <FormLabel justify="start" whiteSpace="nowrap">
        {getLabel(name)}
      </FormLabel>
      <ChakraInput
        value={value || ""}
        onChange={handleChange}
        px={3}
        py={2}
        type={"password"}
        {...(style || field.style || { width: 200 })}
        {...colorMode.input}
      />
    </Flex>
  );
};
