import {
  Badge,
  Box,
  FormControl,
  FormLabel,
  Heading,
  HStack,
  Input,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react";
import React, { useCallback, useContext, useMemo } from "react";
import { TypeAutoFields } from "chains/flow/TypeAutoFields";
import { useDebounce } from "utils/hooks/useDebounce";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { NodeStateContext, SelectedNodeContext } from "chains/editor/contexts";
import { PromptNode } from "chains/flow/PromptNode";
import { FunctionSchemaNode } from "chains/flow/FunctionSchemaNode";
import { CollapsibleSection } from "chains/flow/CollapsibleSection";
import { useNodeEditorAPI } from "chains/hooks/useNodeEditorAPI";

const CONFIG_FORM_COMPONENTS = {
  "langchain.prompts.chat.ChatPromptTemplate": PromptNode,
  "ix.chains.functions.FunctionSchema": FunctionSchemaNode,
};

const NodeGeneralForm = ({ node, onChange }) => {
  const handleNameChange = useCallback(
    (e) => {
      onChange.all({
        ...node,
        name: e.target.value,
      });
    },
    [node, onChange]
  );

  const handleDescriptionChange = useCallback(
    (e) => {
      onChange.all({
        ...node,
        description: e.target.value,
      });
    },
    [node, onChange]
  );

  return (
    <Box>
      <VStack spacing={4} align="stretch">
        <FormControl id="name">
          <FormLabel>Name</FormLabel>
          <Input
            type="text"
            placeholder="Enter node name"
            value={node?.name || ""}
            onChange={handleNameChange}
          />
        </FormControl>
        <FormControl id="description">
          <FormLabel>Description</FormLabel>
          <Textarea
            placeholder="Enter node description"
            value={node?.description || ""}
            onChange={handleDescriptionChange}
          />
        </FormControl>
      </VStack>
    </Box>
  );
};

const DefaultForm = ({ type, node, onChange }) => {
  if (!node) {
    return null;
  }

  return (
    <TypeAutoFields
      type={type}
      config={node.config}
      onChange={onChange.field}
    />
  );
};

/**
 * Hook for a node editor's state. Loads from selected nodes.
 */
export const useNodeEditorState = () => {
  const { nodes } = useContext(NodeStateContext);
  const { selectedNode } = useContext(SelectedNodeContext);
  const data = selectedNode?.data || {};
  const { type } = data;
  const node = nodes && nodes[selectedNode?.id];
  return { type, node };
};

const useNodeName = (type, node) => {
  if (node?.name) {
    return `${node.name}`;
  } else if (type?.name) {
    return type?.name;
  }
  return node?.class_path.split(".").pop();
};

export const ConfigEditorPane = () => {
  const { selectedNode } = useContext(SelectedNodeContext);
  const { setNode } = useContext(NodeStateContext);
  const { type, node } = useNodeEditorState();
  const { highlight } = useEditorColorMode();
  const { handleConfigChange } = useNodeEditorAPI(node, setNode);

  const ConfigForm = CONFIG_FORM_COMPONENTS[type?.class_path] || DefaultForm;
  const name = useNodeName(type, node);

  let content;
  if (selectedNode && node?.config) {
    content = (
      <>
        <CollapsibleSection title="General" mt={3}>
          <NodeGeneralForm node={node} onChange={handleConfigChange} />
        </CollapsibleSection>
        <CollapsibleSection title="Config" initialShow={true} mt={3}>
          {<ConfigForm node={node} type={type} onChange={handleConfigChange} />}
        </CollapsibleSection>
      </>
    );
  } else {
    content = (
      <Text color={"gray.500"} fontSize={"xs"}>
        Select a component node to edit its configuration.
      </Text>
    );
  }

  return (
    <Box>
      <HStack>
        <Badge bg={highlight[type?.type] || highlight.default} size={"xs"}>
          {type?.type}
        </Badge>
        <Heading as="h3" size="md">
          {name}
        </Heading>
      </HStack>
      <Text color={"gray.500"} fontSize={"xs"}>
        {type?.name}
      </Text>
      {content}
    </Box>
  );
};
