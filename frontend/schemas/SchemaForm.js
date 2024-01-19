import React from "react";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  FormHelperText,
  VStack,
  HStack,
  Text,
  useToast,
} from "@chakra-ui/react";

import { useCreateUpdateAPI } from "utils/hooks/useCreateUpdateAPI";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { ModalClose } from "components/Modal";
import { SchemaDeleteButton } from "schemas/SchemaDeleteButton";
import {
  SCHEMA_TYPE_OPTIONS,
  SchemaTypeSelect,
} from "schemas/SchemaTypeSelect";
import OpenAPISchemaForm from "schemas/openapi/OpenAPISchemaForm";
import { OpenAPIFormRightPanel } from "schemas/openapi/OpenAPIFormRightPanel";
import { JSONSchemaFormRightPanel } from "schemas/json/JSONSchemaFormRightPanel";
import JSONSchemaForm from "schemas/json/JSONSchemaForm";

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

export const SchemaForm = ({ forType, schema, onSuccess }) => {
  const toast = useToast();
  const [isEdit, setIsEdit] = React.useState(schema?.id !== undefined);
  const [data, setData] = React.useState(
    schema || {
      name: "",
      description: "",
      type: "openapi",
    }
  );
  const [valid, setValid] = React.useState(true);
  const onClose = React.useContext(ModalClose);
  const style = useEditorColorMode();

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
      onSuccess();
      onClose();
    });
  }, [data, save]);

  // Callback for changing a set of fields in data
  const onDataChange = (updates) => {
    setData((data) => ({ ...data, ...updates }));
  };

  const { Form, Panel } = TYPE_CONFIG[data.type] || {};

  const schema_option = SCHEMA_TYPE_OPTIONS.find(
    (option) => option.value === data.type
  );

  const type_select =
    forType === undefined ? (
      <SchemaTypeSelect
        value={data.type}
        onChange={onDataChange}
        disabled={isEdit}
      />
    ) : (
      <Text
        color="gray.400"
        border={"1px solid"}
        borderRadius={5}
        {...style.input}
        ml={6}
        pl={3}
        py={2}
      >
        {forType}
      </Text>
    );

  return (
    <Box>
      <HStack display={"flex"} alignItems={"start"}>
        <VStack spacing={8} px={3}>
          <FormControl>
            <FormLabel>Type</FormLabel>
            {type_select}
            <FormHelperText fontSize={"xs"}>
              {schema_option.helpText}
            </FormHelperText>
          </FormControl>
          {Form && <Form schema={data} onChange={onDataChange} />}
        </VStack>
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
