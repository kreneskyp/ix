import React from "react";
import {
  Box,
  Flex,
  FormLabel,
  Input as ChakraInput,
  Tooltip,
} from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { getLabel } from "json_form/utils";

export const Input = ({ name, field, isRequired, value, style, onChange }) => {
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
        <Tooltip label={field.description}>
          <Box p={0} m={0}>
            {getLabel(name)}
          </Box>
        </Tooltip>
      </FormLabel>

      <ChakraInput
        value={value || ""}
        onChange={handleChange}
        px={2}
        py={2}
        {...(style || field.style || { width: 200 })}
        {...colorMode.input}
      />
    </Flex>
  );
};
