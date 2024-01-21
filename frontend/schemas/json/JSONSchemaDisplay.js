import React from "react";
import { Box, HStack, Text } from "@chakra-ui/react";

const resolveRef = (ref, schema) => {
  const refPath = ref.replace("#/", "").split("/");
  let definition = schema;
  for (const path of refPath) {
    definition =
      definition[path] ||
      definition.$defs[path] ||
      definition.definitions[path];
    if (!definition) break;
  }
  return definition;
};

const ListWithSeparator = ({ items, separator, style }) => {
  return items.map((item, index) => (
    <React.Fragment key={index}>
      {index > 0 && <span style={{ color: "gray" }}>{separator}</span>}
      <Text as="span" {...style}>
        {item.type}
      </Text>
    </React.Fragment>
  ));
};

const SchemaProperty = ({ name, property, rootSchema }) => {
  const descriptionStyle = { color: "blue.400" }; // Blue styling for property types

  let typeComponent = null;
  let nested = null;
  if (property.properties) {
    nested = (
      <JSONSchemaPropertyList schema={property} rootSchema={rootSchema} />
    );
  } else if (property.$ref) {
    const resolvedRef = resolveRef(property.$ref, rootSchema);
    if (resolvedRef && resolvedRef.properties) {
      nested = (
        <JSONSchemaPropertyList schema={resolvedRef} rootSchema={rootSchema} />
      );
    } else {
      typeComponent = (
        <Text as="span" {...descriptionStyle}>
          {property.$ref}
        </Text>
      );
    }
  } else if (property.anyOf) {
    typeComponent = (
      <ListWithSeparator
        items={property.anyOf}
        separator=" or "
        style={descriptionStyle}
      />
    );
  } else if (property.type) {
    typeComponent = (
      <Text as="span" {...descriptionStyle}>
        {property.type}
      </Text>
    );
  }

  return (
    <>
      <HStack key={name}>
        <Text color={"gray.100"} fontWeight={"bold"}>
          {name}:{" "}
        </Text>
        {typeComponent}
      </HStack>
      {nested && <Box ml={5}>{nested}</Box>}
    </>
  );
};

export const JSONSchemaPropertyList = ({ schema, rootSchema }) => {
  return (
    <>
      {schema.properties &&
        Object.entries(schema.properties).map(([key, value]) => (
          <SchemaProperty
            key={key}
            name={key}
            property={value}
            rootSchema={rootSchema || schema}
          />
        ))}
    </>
  );
};

export const JSONSchemaDisplay = ({ schema, ...props }) => {
  return (
    <Box bg={"gray.800"} p={2} borderRadius={3} {...props}>
      <JSONSchemaPropertyList schema={schema} rootSchema={schema} />
    </Box>
  );
};
