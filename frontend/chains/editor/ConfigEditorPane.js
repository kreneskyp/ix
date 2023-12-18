import { Badge, Box, Center, Heading, HStack, Text } from "@chakra-ui/react";
import React, { useContext } from "react";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { NodeStateContext, SelectedNodeContext } from "chains/editor/contexts";
import { PromptNode } from "chains/flow/PromptNode";
import { FunctionSchemaNode } from "chains/flow/FunctionSchemaNode";
import { CollapsibleSection } from "chains/flow/CollapsibleSection";
import { useNodeEditorAPI } from "chains/hooks/useNodeEditorAPI";
import { NameField } from "chains/editor/fields/NameField";
import { DescriptionField } from "chains/editor/fields/DescriptionField";
import { JSONSchemaForm } from "json_form/JSONSchemaForm";

const CONFIG_FORM_COMPONENTS = {
  "langchain.prompts.chat.ChatPromptTemplate": PromptNode,
  "ix.runnable.prompt.MultiModalChatPrompt": PromptNode,
  "ix.chains.functions.FunctionSchema": FunctionSchemaNode,
  "ix.runnable.schema.Schema": FunctionSchemaNode,
};

const DefaultForm = ({ type, node, onChange }) => {
  if (!node) {
    return null;
  }
  return (
    <JSONSchemaForm
      schema={type?.config_schema}
      data={node.config}
      onChange={onChange.fields}
      defaultLabel={"Config"}
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
  const { highlight, scrollbar } = useEditorColorMode();
  const { handleConfigChange } = useNodeEditorAPI(node, setNode);

  const ConfigForm = CONFIG_FORM_COMPONENTS[type?.class_path] || DefaultForm;
  const name = useNodeName(type, node);

  let content;
  if (selectedNode && node?.config) {
    content = (
      <Box height={"calc(100vh - 150px)"} display={"flex"}>
        <Box width="100%" overflow={"auto"} css={scrollbar} px={3}>
          <CollapsibleSection title="General">
            <NameField object={node} onChange={handleConfigChange.all} />
            <DescriptionField object={node} onChange={handleConfigChange.all} />
          </CollapsibleSection>
          <ConfigForm node={node} type={type} onChange={handleConfigChange} />
        </Box>
      </Box>
    );
  } else {
    content = (
      <Center height={"100%"}>
        <Text color={"gray.500"} fontSize={"xs"}>
          Select a component node to edit its configuration.
        </Text>
      </Center>
    );
  }

  return (
    <Box>
      <Box p={3}>
        <HStack>
          <Badge
            bg={highlight[type?.type] || highlight.default}
            size={"xs"}
            mx={1}
            my={2}
          >
            {type?.type}
          </Badge>
          <Box>
            <Heading as="h3" size="md">
              {name}
            </Heading>
            <Text color={"gray.500"} fontSize={"xs"}>
              {type?.description}
            </Text>
          </Box>
        </HStack>
      </Box>
      {content}
    </Box>
  );
};
