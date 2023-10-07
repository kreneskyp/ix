import React, { useCallback } from "react";
import { FormControl, FormLabel, Textarea } from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const DescriptionField = ({ object, onChange, ...props }) => {
  const colorMode = useEditorColorMode();
  const handleDescriptionChange = useCallback(
    (e) => {
      onChange({
        ...object,
        description: e.target.value,
      });
    },
    [object, onChange]
  );

  return (
    <FormControl id="description">
      <FormLabel>Description</FormLabel>
      <Textarea
        placeholder="Enter description"
        value={object?.description || ""}
        onChange={handleDescriptionChange}
        {...colorMode.input}
        {...props}
      />
    </FormControl>
  );
};
