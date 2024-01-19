import React from "react";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { Box, HStack, Text } from "@chakra-ui/react";

const ListWithSeparator = ({ items, separator }) => {
  return items.map((item, index) => (
    <React.Fragment key={index}>
      {index > 0 && <span style={{ color: "gray" }}>{separator}</span>}
      <Text as="span">{item.type}</Text>
    </React.Fragment>
  ));
};

const SchemaProperty = ({ name, property }) => {
  const { isLight } = useEditorColorMode();
  const descriptionStyle = isLight
    ? { color: "blue.400" }
    : { color: "blue.400" };

  let type = "";
  let nested = null;
  if (property.properties) {
    nested = <JSONSchemaPropertyList schema={property} />;
  } else if (property.$ref) {
    type = property.$ref.split("/").pop();
  } else if (property.anyOf) {
    type = <ListWithSeparator items={property.anyOf} separator=" or " />;
  } else if (property.type) {
    type = property.type;
  }

  return (
    <>
      <HStack key={name}>
        <Text color={"gray.100"} fontWeight={"bold"}>
          {name}:{" "}
        </Text>
        <Text fontSize={"xs"} {...descriptionStyle}>
          {type}
        </Text>
      </HStack>
      {nested && <Box ml={5}>{nested}</Box>}
    </>
  );
};

export const JSONSchemaPropertyList = ({ schema, ...props }) => {
  return (
    <>
      {schema.properties &&
        Object.entries(schema.properties).map(([key, value]) => (
          <SchemaProperty key={key} name={key} property={value} />
        ))}
    </>
  );
};

export const JSONSchemaDisplay = ({ schema, ...props }) => {
  return (
    <Box bg={"gray.800"} p={2} borderRadius={3} {...props}>
      <JSONSchemaPropertyList schema={schema} />
    </Box>
  );
};
