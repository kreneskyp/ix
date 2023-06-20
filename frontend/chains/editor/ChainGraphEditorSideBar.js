import React from "react";

import { HStack, Text, VStack } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBrain,
  faChain,
  faMemory,
  faMessage,
  faRobot,
  faTools,
} from "@fortawesome/free-solid-svg-icons";
import { NodeSelector } from "chains/editor/NodeSelector";
import {
  useEditorColorMode,
  useSideBarColorMode,
} from "chains/editor/useColorMode";
import { usePreloadedQuery } from "react-relay/hooks";
import { NodeTypesQuery } from "chains/graphql/NodeTypesQuery";

export const NodeSelectorHeader = ({ label, icon }) => {
  const { color } = useSideBarColorMode();

  return (
    <HStack
      sx={{ userSelect: "none" }}
      width="100%"
      color={color}
      borderBottom="1px solid"
      borderColor="gray.600"
      px={2}
      pt={1}
    >
      <FontAwesomeIcon icon={icon} />
      <Text>{label}</Text>
    </HStack>
  );
};

export const NodeSelectorList = ({ nodeTypes }) => {
  return (
    <VStack spacing={0}>
      {nodeTypes.map((type, i) => {
        return <NodeSelector key={type.id} type={type} />;
      })}
    </VStack>
  );
};

const filterNodeTypes = (nodeTypes, type) => {
  return nodeTypes.filter((nodeType) => nodeType.type === type);
};

export const ChainGraphEditorSideBar = ({ typesQueryRef }) => {
  const { nodeTypes } = usePreloadedQuery(NodeTypesQuery, typesQueryRef);
  const { highlight } = useEditorColorMode();

  return (
    <VStack justifyItems="left">
      <NodeSelectorHeader
        label="Chain"
        icon={faChain}
        highlight={highlight.chain}
      />
      <NodeSelectorList nodeTypes={filterNodeTypes(nodeTypes, "chain")} />
      <NodeSelectorHeader
        label="LLM"
        icon={faBrain}
        highlight={highlight.llm}
      />
      <NodeSelectorList nodeTypes={filterNodeTypes(nodeTypes, "llm")} />
      <NodeSelectorHeader
        label="Prompts"
        icon={faMessage}
        highlight={highlight.prompt}
      />
      <NodeSelectorList nodeTypes={filterNodeTypes(nodeTypes, "prompt")} />
      <NodeSelectorHeader
        label="Agent"
        icon={faRobot}
        highlight={highlight.agent}
      />
      <NodeSelectorHeader
        label="Memory"
        icon={faMemory}
        highlight={highlight.memory}
      />
      <NodeSelectorList nodeTypes={filterNodeTypes(nodeTypes, "memory")} />
      <NodeSelectorList
        nodeTypes={filterNodeTypes(nodeTypes, "memory_backend")}
      />
      <NodeSelectorHeader
        label="Tool"
        icon={faTools}
        highlight={highlight.tool}
      />
      <NodeSelectorList nodeTypes={filterNodeTypes(nodeTypes, "tools")} />
    </VStack>
  );
};
