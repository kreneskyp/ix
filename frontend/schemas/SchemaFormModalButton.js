import React from "react";
import { SchemaForm } from "schemas/SchemaForm";
import { ModalTrigger, ModalTriggerContent } from "components/Modal";
import { Box } from "@chakra-ui/react";

export const SchemaFormModalButton = ({
  schema,
  onOpen,
  onSuccess,
  children,
}) => {
  return (
    <ModalTrigger
      onOpen={onOpen}
      showClose={false}
      size="6xl"
      title="Edit Schema"
      closeOnBlur={false}
    >
      {children}
      <ModalTriggerContent>
        <Box p={4}>
          <SchemaForm schema={schema} onSuccess={onSuccess} />
        </Box>
      </ModalTriggerContent>
    </ModalTrigger>
  );
};

export default SchemaFormModalButton;
