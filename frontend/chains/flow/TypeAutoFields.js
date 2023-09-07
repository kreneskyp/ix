import React, { useCallback } from "react";
import {
  Checkbox,
  Flex,
  FormLabel,
  HStack,
  Input,
  Select,
  Textarea,
  VStack,
} from "@chakra-ui/react";
import SliderInput from "components/SliderInput";
import { useEditorColorMode } from "chains/editor/useColorMode";

const getLabel = (field) => field.label || labelify(field.name || "");

const AutoFieldCheckbox = ({ field, value, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = useCallback(
    (event) => {
      onChange(field.name, event.target.checked);
    },
    [field, onChange]
  );

  return (
    <HStack width="100%">
      <FormLabel justify="start">{getLabel(field)}</FormLabel>
      <Checkbox
        isChecked={value}
        onChange={handleChange}
        {...colorMode.input}
      />
    </HStack>
  );
};

const AutoFieldInput = ({ field, value, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = useCallback(
    (event) => {
      onChange(field.name, event.target.value);
    },
    [field, onChange]
  );

  return (
    <Flex justifyContent="space-between" wrap="wrap" width="100%">
      <FormLabel justify="start" whiteSpace="nowrap">
        {getLabel(field)}
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

const AutoFieldSecret = ({ field, value, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = useCallback(
    (event) => {
      onChange(field.name, event.target.value);
    },
    [field, onChange]
  );

  return (
    <Flex justifyContent="space-between" wrap="wrap" width="100%">
      <FormLabel justify="start" whiteSpace="nowrap">
        {getLabel(field)}
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

const AutoFieldTextArea = ({ field, value, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = useCallback(
    (event) => {
      onChange(field.name, event.target.value);
    },
    [field, onChange]
  );

  return (
    <Flex justifyContent="space-between" wrap="wrap" width="100%">
      <FormLabel justify="start" whiteSpace="nowrap">
        {getLabel(field)}
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

const AutoFieldSlider = ({ field, value, onChange }) => {
  const handleChange = useCallback(
    (newValue) => {
      onChange(field.name, newValue);
    },
    [field, onChange]
  );

  return (
    <SliderInput
      label={getLabel(field)}
      field={field.name}
      value={value}
      onChange={handleChange}
      min={field.min}
      max={field.max}
      step={field.step}
    />
  );
};

const AutoFieldSelect = ({ field, value, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = useCallback((event) => {
    onChange(field.name, event.target.value);
  });

  return (
    <Flex width="100%" justifyContent="space-between">
      <FormLabel size="sm" justify="start">
        {getLabel(field)}
      </FormLabel>
      <Select
        onChange={handleChange}
        width={field.width || 125}
        value={value}
        {...colorMode.input}
      >
        {field.choices?.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </Select>
    </Flex>
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
};

// type specific default inputs
const TYPE_INPUTS = {
  boolean: "checkbox",
  bool: "checkbox",
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
};

export const getDefaults = (nodeType) => {
  const defaults = {};
  nodeType.fields?.forEach(
    (field) =>
      (defaults[field.name] = field.default || FIELD_TYPE_DEFAULTS[field.type])
  );
  return defaults;
};
export const TypeAutoField = ({ field, config, onChange }) => {
  // Select component based on explicit input type, field type, or default in that order.
  const FieldComponent =
    INPUTS[field.input_type || TYPE_INPUTS[field.type]] || DEFAULT_COMPONENT;
  const value =
    config && field.name in config ? config[field.name] : field.default;

  return <FieldComponent field={field} value={value} onChange={onChange} />;
};

export const TypeAutoFields = ({ type, config, onChange }) => {
  return (
    <VStack spacing={1} width="100%">
      {type.fields?.map((field) => (
        <TypeAutoField
          key={field.name}
          field={field}
          config={config}
          onChange={onChange}
        />
      ))}
    </VStack>
  );
};
