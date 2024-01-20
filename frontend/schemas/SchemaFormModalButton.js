import React from "react";
import { SchemaForm } from "schemas/SchemaForm";
import { ModalTrigger, ModalTriggerContent } from "components/Modal";
import { Box } from "@chakra-ui/react";

const TITLES = {
  json: "Edit Schema",
  openapi: "Edit OpenAPI Spec",
};

export const SchemaFormModalButton = ({
  schema,
  onOpen,
  onSuccess,
  children,
  type,
}) => {
  return (
    <ModalTrigger
      onOpen={onOpen}
      showClose={false}
      size="6xl"
      title={TITLES[type] || "Edit Schema"}
      closeOnBlur={false}
    >
      {children}
      <ModalTriggerContent>
        <Box p={4}>
          <SchemaForm schema={schema} type={type} onSuccess={onSuccess} />
        </Box>
      </ModalTriggerContent>
    </ModalTrigger>
  );
};

export default SchemaFormModalButton;
