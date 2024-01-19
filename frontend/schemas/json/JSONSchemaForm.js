import React from "react";
import { VStack } from "@chakra-ui/react";
import { NameField } from "chains/editor/fields/NameField";
import { DescriptionField } from "chains/editor/fields/DescriptionField";

export const JSONSchemaForm = ({ schema, onChange, ...props }) => {
  return (
    <VStack spacing={4} align="stretch" width={"100%"} {...props}>
      <NameField
        onChange={onChange}
        object={schema}
        isDisabled={schema === undefined}
      />
      <DescriptionField
        onChange={onChange}
        isDisabled={schema === undefined}
        object={schema}
      />
    </VStack>
  );
};

export default JSONSchemaForm;
