import React from "react";
import axios from "axios";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  FormHelperText,
  Input,
  VStack,
  HStack,
  Text,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faLock } from "@fortawesome/free-solid-svg-icons";

import { useCreateUpdateAPI } from "utils/hooks/useCreateUpdateAPI";
import { DictForm } from "components/DictForm";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { ModalClose } from "components/Modal";
import { SecretsDeleteButton } from "secrets/SecretsDeleteButton";
import { SecretTypeSelect } from "secrets/SecretTypeSelect";
import { useDetailAPI } from "utils/hooks/useDetailAPI";
import { JSONSchemaForm } from "json_form/JSONSchemaForm";

export const SecretsForm = ({ forType, secret, onSuccess }) => {
  const [isEdit, setIsEdit] = React.useState(secret?.id !== undefined);
  const [data, setData] = React.useState(secret || {});
  const [type, setType] = React.useState(null);
  const [newType, setNewType] = React.useState(false);
  const [valid, setValid] = React.useState(true);
  const onClose = React.useContext(ModalClose);
  const style = useEditorColorMode();

  const { save } = useCreateUpdateAPI(
    "/api/secrets/",
    `/api/secrets/${secret?.id}`
  );

  // auto "select" the forType when it is passed in
  React.useEffect(() => {
    if (forType) {
      const load_for_type = async () => {
        const response = await axios.get(
          `/api/secret_types/?limit=20&key=${forType}`
        );
        if (response.data.count === 0) {
          throw Error("No secret type found for key: " + forType);
        } else if (response.data.count > 1) {
          console.warn("More than one secret type found for key: " + forType);
        }
        setType(response.data.objects[0]);
        setData((data) => ({ ...data, type_id: response.data.objects[0].id }));
      };
      load_for_type().catch((err) => {
        console.error("failed to load secret type", err);
      });
    }
  }, [forType]);

  const typeApi = useDetailAPI(`/api/secret_types/${data?.type_id}`);

  // fetch the type when there is a type selected
  React.useEffect(() => {
    if (data?.type_id && forType === undefined) {
      typeApi.call().then((response) => {
        setType(response.data);
      });
    }
  }, [data?.type_id]);

  const onSave = React.useCallback(() => {
    // remove blank values from data.value
    const value = Object.fromEntries(
      Object.entries(data.value || {}).filter(([key, value]) => value !== "")
    );

    save({ ...data, value }).then(() => {
      onSuccess();
      onClose();
    });
  }, [data, save]);

  // Callback for changing a set of fields in data
  const onDataChange = (updates) => {
    setData((data) => ({ ...data, ...updates }));
  };

  const onNameChange = (e) => {
    setData((data) => ({ ...data, name: e.target.value }));
  };

  // callback to replace the entire value dict
  const onValueChange = (value) => {
    setData((data) => ({ ...data, value }));
  };

  // callback to change a single field in the value dict
  const onValueFieldsChange = React.useCallback(
    (values) => {
      setData((data) => ({ ...data, value: { ...data.value, ...values } }));
    },
    [data?.value]
  );

  let form = null;
  if (data?.type_id && type) {
    form = (
      <Box p={0} mr={5}>
        <JSONSchemaForm
          schema={type.fields_schema}
          data={data?.value || {}}
          onChange={onValueFieldsChange}
          global={{
            input_type: "secret",
            style: {
              width: "100%",
              placeholder: isEdit ? "*************" : "enter value",
            },
          }}
        />
      </Box>
    );
  } else if (newType) {
    form = (
      <>
        <DictForm
          dict={data?.value || {}}
          onChange={onValueChange}
          label="Value"
          {...style.input}
          value_props={{
            type: "password",
          }}
        />
        <FormHelperText fontSize="xs">
          Enter key and value pairs to store in the secret. Example: API_KEY =
          123456
        </FormHelperText>
      </>
    );
  }

  const secret_select =
    forType === undefined ? (
      <SecretTypeSelect
        data={data || {}}
        onChange={onDataChange}
        onNew={(value) => {
          setNewType(value);
        }}
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
      <VStack spacing={5}>
        <FormControl pr={6}>
          <FormLabel pl={6}>Type</FormLabel>
          {secret_select}
        </FormControl>
        <FormControl px={6}>
          <FormLabel>Name</FormLabel>
          <Input
            value={data?.name || "default"}
            onChange={onNameChange}
            placeholder="Enter name"
            {...style.input}
          />
          <FormHelperText fontSize="xs">
            Enter a unique name to identify the secret, example: github_1,
            github_2
          </FormHelperText>
        </FormControl>
        <FormControl pl={6} pr={1}>
          {form}
        </FormControl>
        <HStack m={5} px={5}>
          <FontAwesomeIcon icon={faLock} style={{ marginRight: 3 }} />
          <Text>
            Secrets will not be displayed again after they are saved to secure
            storage.
          </Text>
        </HStack>
      </VStack>

      <HStack display="flex" justifyContent="flex-end" mt={4} mr={7}>
        {secret?.id && (
          <SecretsDeleteButton secret={secret} onSuccess={onSuccess} />
        )}
        <Button colorScheme="blue" onClick={onSave} isDisabled={!valid}>
          Save
        </Button>
        <Button onClick={onClose}>Close</Button>
      </HStack>
    </Box>
  );
};
