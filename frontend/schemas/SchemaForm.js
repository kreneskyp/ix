import React from "react";
import { Box, Button, HStack, useToast } from "@chakra-ui/react";

import { useCreateUpdateAPI } from "utils/hooks/useCreateUpdateAPI";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { ModalClose } from "components/Modal";
import { SchemaDeleteButton } from "schemas/SchemaDeleteButton";
import OpenAPISchemaForm from "schemas/openapi/OpenAPISchemaForm";
import { OpenAPIFormRightPanel } from "schemas/openapi/OpenAPIFormRightPanel";
import { JSONSchemaFormRightPanel } from "schemas/json/JSONSchemaFormRightPanel";
import JSONSchemaForm from "schemas/json/JSONSchemaForm";
import { JSONSchemaIcon } from "icons/JSONSchemaIcon";
import { OpenAPIIcon } from "icons/OpenAPIIcon";

const TYPE_CONFIG = {
  json: {
    Form: JSONSchemaForm,
    Panel: JSONSchemaFormRightPanel,
  },
  openapi: {
    Form: OpenAPISchemaForm,
    Panel: OpenAPIFormRightPanel,
  },
};

const JSON_HELP_TEXT = "Schema for data generation, extraction, and validation";
const OPENAPI_HELP_TEXT = "Schema for API access";

export const SCHEMA_TYPE_OPTIONS = [
  {
    value: "json",
    label: "JSON",
    helpText: JSON_HELP_TEXT,
    icon: { component: JSONSchemaIcon },
  },
  {
    value: "openapi",
    label: "OpenAPI",
    helpText: OPENAPI_HELP_TEXT,
    icon: { component: OpenAPIIcon },
  },
];

export const SchemaForm = ({ type, schema, onSuccess }) => {
  const toast = useToast();
  const [isEdit, setIsEdit] = React.useState(schema?.id !== undefined);
  const [data, setData] = React.useState(
    schema || {
      name: "",
      description: "",
      type: type,
    }
  );
  const [valid, setValid] = React.useState(true);
  const onClose = React.useContext(ModalClose);

  const { save } = useCreateUpdateAPI(
    "/api/schemas/",
    `/api/schemas/${schema?.id}`
  );

  const onSave = React.useCallback(() => {
    save({ ...data }).then((response) => {
      toast({
        title: "Schema saved",
        description: `${data.name} saved`,
        status: "success",
        duration: 2000,
        isClosable: true,
        position: "bottom-right",
      });
      onSuccess(response);
      onClose();
    });
  }, [data, save]);

  // Callback for changing a set of fields in data
  const onDataChange = (updates) => {
    setData((data) => ({ ...data, ...updates }));
  };

  const { Form, Panel } = TYPE_CONFIG[data.type] || {};

  return (
    <Box>
      <HStack display={"flex"} alignItems={"start"} pr={3}>
        <Box pl={2} width={500}>
          {Form && (
            <Form width={500} pr={5} schema={data} onChange={onDataChange} />
          )}
        </Box>
        {Panel && <Panel schema={data} onChange={onDataChange} />}
      </HStack>
      <HStack display="flex" justifyContent="flex-end" mt={4} mr={7}>
        {schema?.id && (
          <SchemaDeleteButton schema={schema} onSuccess={onSuccess} />
        )}
        <Button colorScheme="blue" onClick={onSave} isDisabled={!valid}>
          Save
        </Button>
        <Button onClick={onClose}>Close</Button>
      </HStack>
    </Box>
  );
};
