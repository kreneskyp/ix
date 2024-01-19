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
import { SecretSelect } from "json_form/fields/SecretSelect";
import { useDisplayGroups } from "chains/hooks/useDisplayGroups";
import { CollapsibleSection } from "chains/flow/CollapsibleSection";
import { APISelect } from "json_form/fields/APISelect";
import { ChainSelect } from "chains/ChainSelect";
import { HashList } from "json_form/fields/HashList";
import { BranchesField } from "chains/editor/fields/BranchesField";
import { MapField } from "chains/editor/fields/MapField";
import { SchemaSelect } from "schemas/SchemaSelect";
import { SchemaActionSelect } from "schemas/openapi/SchemaActionSelect";
import { SchemaServerSelect } from "schemas/openapi/SchemaServerSelect";
import { JSONSchemaSelect } from "schemas/json/JSONSchemaSelect";
import { OpenAPISchemaSelect } from "schemas/openapi/OpenAPISchemaSelect";

// explicit input types
const INPUTS = {
  select: Select,
  checkbox: Checkbox,
  slider: Slider,
  input: Input,
  secret: Secret,
  secret_select: SecretSelect,
  textarea: TextArea,
  dict: Dict,
  list: List,
  "IX:chain": APISelect.for_select(ChainSelect),
  "IX:json_schema": APISelect.for_select(JSONSchemaSelect),
  "IX:openapi_schema": APISelect.for_select(OpenAPISchemaSelect),
  "IX:openapi_action": APISelect.for_select(SchemaActionSelect),
  "IX:openapi_server": APISelect.for_select(SchemaServerSelect),
  hash_list: HashList,
  node_branch_list: BranchesField,
  node_map_list: MapField,
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

export const AutoField = ({
  name,
  field,
  isRequired,
  config,
  global,
  onChange,
}) => {
  // Select component based on explicit input type, field type, or default in that order.
  const input_key =
    global?.input_type || field.input_type || TYPE_INPUTS[field.type];

  // do not render hidden fields
  if (input_key === "hidden") {
    return null;
  }
  const FieldComponent = INPUTS[input_key] || Input;
  const value = config && name in config ? config[name] : field.default;

  // repackage style prop from field to include global options
  const style = global.style || field.style;

  return (
    <FormControl>
      <HStack>
        <FieldComponent
          name={name}
          field={field}
          isRequired={isRequired}
          value={value}
          config={config}
          onChange={onChange}
          style={style}
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

const SectionFields = ({ schema, global, config, onChange }) => {
  // use schema's order if defined, else alphabetical
  const order = schema.order || Object.keys(schema.properties).sort();

  return (
    <VStack spacing={3} width="100%">
      {order.map((key) => {
        const property = schema.properties[key];
        // HAX: disabling isRequired now since some configs are marking every field as required
        const isRequired = schema.required?.includes(key);
        return (
          <AutoField
            key={key}
            field={property}
            name={key}
            isRequired={false}
            config={config}
            onChange={onChange}
            global={global}
          />
        );
      })}
    </VStack>
  );
};

const CollapsibleFormSection = ({
  schema,
  title,
  config,
  global,
  initialShow,
  onChange,
}) => {
  return (
    <CollapsibleSection
      key={title}
      title={title}
      initialShow={initialShow}
      mt={3}
    >
      <SectionFields
        schema={schema}
        config={config}
        global={global}
        onChange={onChange}
      />
    </CollapsibleSection>
  );
};

export const JSONSchemaForm = ({
  schema,
  data,
  global,
  defaultLabel,
  groupProperties,
  onChange,
}) => {
  if (groupProperties) {
    // get sub-schemas for each group
    const groupSchemas = useDisplayGroups(schema);

    return (
      <>
        {Object.keys(groupSchemas).map((groupKey, i) => {
          const groupSchema = groupSchemas[groupKey];
          return (
            <CollapsibleFormSection
              key={groupKey}
              title={
                groupKey === "default" && defaultLabel ? defaultLabel : groupKey
              }
              schema={groupSchema}
              global={global}
              config={data}
              onChange={onChange}
              initialShow={i === 0}
            />
          );
        })}
      </>
    );
  } else {
    return (
      <SectionFields
        schema={schema}
        properties={schema.properties}
        config={data}
        global={global}
        onChange={onChange}
      />
    );
  }
};

JSONSchemaForm.defaultProps = {
  groupProperties: true,
  global: {},
};
