import React, { useCallback } from "react";
import { FormControl, FormLabel, Input } from "@chakra-ui/react";

export const NameField = ({ object, onChange }) => {
  const handleNameChange = useCallback(
    (e) => {
      onChange({
        ...object,
        name: e.target.value,
      });
    },
    [object, onChange]
  );

  return (
    <FormControl id="name">
      <FormLabel>Name</FormLabel>
      <Input
        type="text"
        placeholder="Enter name"
        value={object?.name || ""}
        onChange={handleNameChange}
      />
    </FormControl>
  );
};
