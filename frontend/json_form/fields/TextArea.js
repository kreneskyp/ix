import React from "react";
import { Flex, FormLabel, Textarea } from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { getLabel } from "json_form/utils";

export const TextArea = ({ name, field, isRequired, value, onChange }) => {
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
      <Textarea
        fontSize="sm"
        value={value}
        onChange={handleChange}
        px={1}
        py={2}
        sx={field.style || { width: 200 }}
        {...colorMode.input}
      />
    </Flex>
  );
};
