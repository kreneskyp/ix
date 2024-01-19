import React from "react";
import { Box, HStack, Badge, Text } from "@chakra-ui/react";
import { CollapsibleSection } from "chains/flow/CollapsibleSection";
import { useEditorColorMode } from "chains/editor/useColorMode";

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

const SchemaPath = ({ path, method, methodInfo }) => {
  const { isLight } = useEditorColorMode();
  const descriptionStyle = isLight
    ? { color: "gray.700" }
    : { color: "gray.500" };

  return (
    <HStack key={path}>
      <Badge
        bg={METHOD_COLORS[method]}
        color={"white"}
        width={12}
        alignItems={"center"}
      >
        {method}
      </Badge>
      <Text>{path}</Text>
      <Text fontSize={"xs"} {...descriptionStyle}>
        {methodInfo.summary}
      </Text>
    </HStack>
  );
};

export const SchemaPathsList = ({ schema }) => {
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

  return (
    <Box>
      {Object.keys(pathsByTag).map((tag) => (
        <CollapsibleSection key={tag} title={tag} mb={2}>
          {pathsByTag[tag].map((endpoint, i) => (
            <SchemaPath key={i} {...endpoint} />
          ))}
        </CollapsibleSection>
      ))}
    </Box>
  );
};

export default SchemaPathsList;
