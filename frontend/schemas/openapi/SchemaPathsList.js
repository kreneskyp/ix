import React from "react";
import { Box, HStack, Badge, Text } from "@chakra-ui/react";
import { CollapsibleSection } from "chains/flow/CollapsibleSection";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { DraggableNode } from "chains/editor/DraggableNode";
import { labelify } from "json_form/utils";
import { DRAGGABLE_CONFIG } from "schemas/openapi/OpenAPIDraggable";

export const METHOD_COLORS = {
  get: "green.400",
  post: "blue.400",
  put: "orange.400",
  delete: "red.400",
  patch: "purple.300",
  options: "gray.300",
  head: "gray.300",
  trace: "gray.300",
};

const SchemaPath = ({ schema_id, server, path, method, methodInfo }) => {
  const { isLight } = useEditorColorMode();
  const descriptionStyle = isLight
    ? { color: "gray.700" }
    : { color: "gray.500" };

  return (
    <HStack key={path}>
      <DraggableNode
        name={`${methodInfo.operationId}`}
        description={methodInfo.summary}
        config={{ schema_id, server, path, method }}
        class_path={DRAGGABLE_CONFIG.class_path}
      >
        <Badge
          bg={METHOD_COLORS[method]}
          color={"white"}
          width={12}
          alignItems={"center"}
          zIndex={1}
        >
          {method}
        </Badge>
      </DraggableNode>
      <Text>{path}</Text>
      <Text fontSize={"xs"} {...descriptionStyle}>
        {methodInfo.summary}
      </Text>
    </HStack>
  );
};

export const SchemaPathsList = ({ schema, schema_id }) => {
  // Organize paths by tag
  const pathsByTag = React.useMemo(() => {
    const byTag = {};
    Object.keys(schema.paths).forEach((path) => {
      const pathInfo = schema.paths[path];
      Object.keys(pathInfo).forEach((method) => {
        const methodInfo = pathInfo[method];
        const tag = methodInfo.tags ? methodInfo.tags[0] : "Other";
        if (!byTag[tag]) {
          byTag[tag] = [];
        }
        byTag[tag].push({
          path,
          method,
          methodInfo,
        });
      });
    });
    return byTag;
  }, [schema]);

  console.log("::Schema: ", schema);

  return (
    <Box>
      {Object.keys(pathsByTag).map((tag) => (
        <CollapsibleSection key={tag} title={tag} mb={2}>
          {pathsByTag[tag].map((endpoint, i) => (
            <SchemaPath
              key={i}
              {...endpoint}
              schema_id={schema_id}
              server={schema.servers[0]?.url}
            />
          ))}
        </CollapsibleSection>
      ))}
    </Box>
  );
};

export default SchemaPathsList;
