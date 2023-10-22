import React, { useCallback } from "react";
import {
  Box,
  Checkbox,
  Flex,
  FormControl,
  FormLabel,
  HStack,
  Input,
  Select,
  Textarea,
  Tooltip,
  VStack,
} from "@chakra-ui/react";
import SliderInput from "components/SliderInput";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { DictForm } from "components/DictForm";
import { ListForm } from "components/ListForm";

const getLabel = (name) => name || labelify(name || "");

const AutoFieldCheckbox = ({ name, field, value, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = useCallback(
    (event) => {
      onChange(name, event.target.checked);
    },
    [field, onChange]
  );

  return (
    <HStack width="100%">
      <FormLabel justify="start">{getLabel(name)}</FormLabel>
      <Checkbox
        isChecked={value}
        onChange={handleChange}
        {...colorMode.input}
      />
    </HStack>
  );
};

const AutoFieldInput = ({ name, field, isRequired, value, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = useCallback(
    (event) => {
      onChange(name, event.target.value);
    },
    [field, onChange]
  );

  return (
    <Flex justifyContent="space-between" wrap="wrap" width="100%">
      <FormLabel justify="start" whiteSpace="nowrap">
        <Tooltip label={field.description}>
          <Box p={0} m={0}>
            {getLabel(name)}
          </Box>
        </Tooltip>
      </FormLabel>

      <Input
        value={value || ""}
        onChange={handleChange}
        px={2}
        py={2}
        sx={field.style || { width: 200 }}
        {...colorMode.input}
      />
    </Flex>
  );
};

const AutoFieldSecret = ({ name, field, isRequired, value, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = useCallback(
    (event) => {
      onChange(name, event.target.value);
    },
    [field, onChange]
  );

  return (
    <Flex justifyContent="space-between" wrap="wrap" width="100%">
      <FormLabel justify="start" whiteSpace="nowrap">
        {getLabel(name)}
      </FormLabel>
      <Input
        value={value || ""}
        onChange={handleChange}
        px={1}
        py={2}
        type={"password"}
        sx={field.style || { width: 200 }}
        {...colorMode.input}
      />
    </Flex>
  );
};

const AutoFieldTextArea = ({ name, field, isRequired, value, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = useCallback(
    (event) => {
      onChange(name, event.target.value);
    },
    [field, onChange]
  );

  return (
    <Flex justifyContent="space-between" wrap="wrap" width="100%">
      <FormLabel justify="start" whiteSpace="nowrap">
        {getLabel(name)}
      </FormLabel>
      <Textarea
        fontSize="sm"
        value={value}
        onChange={handleChange}
        px={1}
        py={2}
        sx={field.style || { width: 200 }}
        {...colorMode.input}
      />
    </Flex>
  );
};

const AutoFieldSlider = ({ name, field, value, onChange }) => {
  const handleChange = useCallback(
    (newValue) => {
      onChange(name, newValue);
    },
    [field, onChange]
  );

  return (
    <SliderInput
      label={getLabel(name)}
      field={name}
      value={value}
      onChange={handleChange}
      min={field.minimum}
      max={field.maximum}
      step={field.multipleOf}
    />
  );
};

const AutoFieldSelect = ({ name, field, isRequired, value, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = useCallback((event) => {
    onChange(name, event.target.value);
  });

  return (
    <Flex width="100%" justifyContent="space-between">
      <FormLabel size="sm" justify="start">
        {getLabel(name)}
      </FormLabel>
      <Select
        onChange={handleChange}
        width={field.width || 200}
        value={value}
        {...colorMode.input}
      >
        {field.enum?.map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </Select>
    </Flex>
  );
};

const AutoFieldDict = ({ name, field, isRequired, value, onChange }) => {
  const handleChange = useCallback(
    (newValue) => {
      // Check if newValue is null or undefined, if so, set it to an empty object
      newValue = newValue || {};
      onChange(name, newValue);
    },
    [field, onChange]
  );

  // Check if value is null or undefined, if so, set it to an empty object
  value = value || {};

  return (
    <DictForm
      dict={value}
      onChange={handleChange}
      label={getLabel(name)}
      isRequired
    />
  );
};

const AutoFieldList = ({ name, field, isRequired, value, onChange }) => {
  const handleChange = useCallback(
    (newValue) => {
      // Check if newValue is null or undefined, if so, set it to an empty array
      newValue = newValue || [];
      onChange(name, newValue);
    },
    [field, onChange]
  );

  // Check if value is null or undefined, if so, set it to an empty array
  value = value || [];

  return (
    <ListForm
      list={value}
      onChange={handleChange}
      label={getLabel(name)}
      isRequired
    />
  );
};

// explicit input types
const INPUTS = {
  select: AutoFieldSelect,
  checkbox: AutoFieldCheckbox,
  slider: AutoFieldSlider,
  input: AutoFieldInput,
  secret: AutoFieldSecret,
  textarea: AutoFieldTextArea,
  dict: AutoFieldDict,
  list: AutoFieldList,
};

// type specific default inputs
const TYPE_INPUTS = {
  boolean: "checkbox",
  bool: "checkbox",
  dict: "dict",
  list: "list",
  array: "list",
  object: "dict",
};

const DEFAULT_COMPONENT = AutoFieldInput;

const labelify = (key) => {
  return key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
};

const FIELD_TYPE_DEFAULTS = {
  boolean: false,
  number: 0,
  string: "",
  list: [],
  dict: {},
  object: {},
};

// This is used elsewhere in graph editor
export const getDefaults = (nodeType) => {
  const defaults = {};
  nodeType.fields?.forEach(
    (field) =>
      (defaults[name] = field.default || FIELD_TYPE_DEFAULTS[field.type])
  );
  return defaults;
};

export const TypeAutoField = ({
  name,
  field,
  isRequired,
  config,
  onChange,
}) => {
  // Select component based on explicit input type, field type, or default in that order.
  const FieldComponent =
    INPUTS[field.input_type || TYPE_INPUTS[field.type]] || DEFAULT_COMPONENT;
  const value = config && name in config ? config[name] : field.default;

  return (
    <FormControl>
      <HStack>
        <FieldComponent
          name={name}
          field={field}
          isRequired={isRequired}
          value={value}
          onChange={onChange}
        />
      </HStack>
    </FormControl>
  );
};

export const JSONSchemaForm = ({ schema, data, onChange }) => {
  return (
    <VStack spacing={3} width="100%">
      {Object.keys(schema?.properties).map((fieldName) => {
        const field = schema.properties[fieldName];
        return (
          <TypeAutoField
            key={fieldName}
            field={field}
            name={fieldName}
            isRequired={schema.required.includes(fieldName)}
            config={data}
            onChange={onChange}
          />
        );
      })}
    </VStack>
  );
};

export const TypeAutoFields = ({ type, config, onChange }) => {
  return (
    <JSONSchemaForm
      schema={type?.config_schema}
      data={config}
      onChange={onChange}
    />
  );
};
