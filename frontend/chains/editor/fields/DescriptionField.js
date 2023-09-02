import React, { useCallback } from "react";
import { FormControl, FormLabel, Textarea } from "@chakra-ui/react";

export const DescriptionField = ({ object, onChange }) => {
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
      />
    </FormControl>
  );
};
