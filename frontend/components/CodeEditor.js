import React from "react";
import {
  FormControl,
  FormErrorMessage,
  FormHelperText,
  FormLabel,
  Textarea,
} from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { RequiredAsterisk } from "components/RequiredAsterisk";

const CodeEditor = ({
  label,
  value,
  onChange,
  error,
  required,
  help,
  ...props
}) => {
  const { code, scrollbar, input } = useEditorColorMode();

  const handleChange = React.useCallback(
    (e) => {
      onChange(e.target.value);
    },
    [onChange]
  );

  return (
    <FormControl isInvalid={error !== undefined}>
      <FormLabel justify="start">
        {label} {required === true && <RequiredAsterisk />}
      </FormLabel>
      <Textarea
        value={value}
        onChange={handleChange}
        color={code.color}
        bg={code.bg}
        fontFamily="monospace"
        fontSize="sm"
        {...input}
        css={scrollbar}
        height={400}
        width={"100%"}
        {...props}
      />
      {help && <FormHelperText>{help}</FormHelperText>}
      {error && <FormErrorMessage>{error}</FormErrorMessage>}
    </FormControl>
  );
};

export default CodeEditor;
