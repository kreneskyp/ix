import { Badge, Box, Divider, Flex, Heading, Text } from "@chakra-ui/react";
import React, { useContext, useMemo } from "react";
import { TypeAutoFields } from "chains/flow/TypeAutoFields";
import { useDebounce } from "utils/hooks/useDebounce";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { DEFAULT_NODE_STYLE, NODE_STYLES } from "chains/editor/styles";
import { SelectedNodeContext } from "chains/editor/SelectedNodeContext";

export const ChainEditorRightPane = () => {
  const api = useContext(ChainEditorAPIContext);
  const { config, setConfig, selectedNode } = useContext(SelectedNodeContext);
  const { highlight } = useEditorColorMode();

  const { callback: debouncedUpdateNode } = useDebounce(api.updateNode, 1000);
  const handleConfigChange = useMemo(() => {
    function all(newConfig, delay = 0) {
      const data = {
        class_path: node.class_path,
        description: node.description,
        position: node.position,
        config: newConfig,
      };
      debouncedUpdateNode(node.id, data);
      setConfig(newConfig);
    }

    const field = (key, value, delay = 1000) => {
      const newConfig = { ...config.current, [key]: value };
      all(newConfig, delay);
    };

    return { all, field };
  }, [selectedNode, api]);

  const styles = NODE_STYLES[type?.type] || DEFAULT_NODE_STYLE;

  const data = selectedNode?.data || {};
  const { type, node } = data;
  return (
    <Box>
      <Heading as="h3" size="md">
        {node?.name || type?.name || node?.class_path.split(".").pop()}
      </Heading>
      <Badge bg={highlight[type?.type] || highlight.default}>
        {type?.type}
      </Badge>
      <Divider my={3} />

      {node && (
        <TypeAutoFields
          type={type}
          config={config}
          onFieldChange={handleConfigChange.field}
        />
      )}
    </Box>
  );
};
