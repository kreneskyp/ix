import React from "react";
import { FormControl, HStack, VStack } from "@chakra-ui/react";
import { Select } from "json_form/fields/Select";
import { Checkbox } from "json_form/fields/Checkbox";
import { Slider } from "json_form/fields/Slider";
import { Input } from "json_form/fields/Input";
import { Secret } from "json_form/fields/Secret";
import { TextArea } from "json_form/fields/TextArea";
import { Dict } from "json_form/fields/Dict";
import { List } from "json_form/fields/List";

// explicit input types
const INPUTS = {
  select: Select,
  checkbox: Checkbox,
  slider: Slider,
  input: Input,
  secret: Secret,
  textarea: TextArea,
  dict: Dict,
  list: List,
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

export const NOOP = ({}) => <div>NOOP</div>;

export const AutoField = ({ name, field, isRequired, config, onChange }) => {
  // Select component based on explicit input type, field type, or default in that order.
  const input_key = field.input_type || TYPE_INPUTS[field.type];
  const FieldComponent = INPUTS[input_key] || Input;
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
      (defaults[field.name] = field.default || FIELD_TYPE_DEFAULTS[field.type])
  );
  return defaults;
};

export const JSONSchemaForm = ({ schema, data, onChange }) => {
  return (
    <VStack spacing={3} width="100%">
      {Object.keys(schema?.properties).map((fieldName) => {
        const field = schema.properties[fieldName];
        return (
          <AutoField
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
