import React from "react";
import { Flex, FormLabel, Select as ChakraSelect } from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { getLabel } from "json_form/utils";

export const Select = ({ name, field, isRequired, value, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = React.useCallback((event) => {
    onChange(name, event.target.value);
  });

  return (
    <Flex width="100%" justifyContent="space-between">
      <FormLabel size="sm" justify="start">
        {getLabel(name)}
      </FormLabel>
      <ChakraSelect
        onChange={handleChange}
        width={field?.width || 200}
        value={value}
        {...colorMode.input}
      >
        {field?.enum?.map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </ChakraSelect>
    </Flex>
  );
};
