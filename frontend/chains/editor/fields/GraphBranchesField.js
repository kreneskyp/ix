import React from "react";
import { Box, Textarea, Input } from "@chakra-ui/react";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { BranchesField } from "chains/editor/fields/BranchesField";

const useAsEvent = (handler) => {
  return React.useCallback(
    (value) => handler({ target: { value } }),
    [handler]
  );
};

export const BranchField = ({ value, onChange }) => {
  const colorMode = useEditorColorMode();

  const handleChange = useAsEvent(onChange);
  const handleDescriptionChange = React.useCallback(
    (e) => {
      handleChange({
        ...value,
        description: e.target.value,
      });
    },
    [value, handleChange]
  );

  const handleNameChange = React.useCallback(
    (e) => {
      handleChange({
        ...value,
        name: e.target.value,
      });
    },
    [value, handleChange]
  );

  return (
    <Box width={"100%"}>
      <Input
        type="text"
        placeholder="Enter name"
        value={value?.name || ""}
        onChange={handleNameChange}
        {...colorMode.input}
      />
      <Textarea
        placeholder="Describe when and how to use this branch"
        value={value?.description || ""}
        onChange={handleDescriptionChange}
        css={colorMode.scrollbar}
        {...colorMode.input}
      />
    </Box>
  );
};

export const GraphBranchesField = ({ ...props }) => {
  return <BranchesField {...props} component={BranchField} />;
};
