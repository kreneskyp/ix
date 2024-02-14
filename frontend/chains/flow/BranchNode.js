import React, { useMemo } from "react";
import { Handle, useEdges } from "reactflow";
import { Box, VStack, Heading, Flex } from "@chakra-ui/react";
import { useConnectorColor } from "chains/flow/ConfigNode";
import { RequiredAsterisk } from "components/RequiredAsterisk";
import { ConnectorPopover } from "chains/editor/ConnectorPopover";

const useFlowConnectors = (node) => {
  const edges = useEdges();
  return useMemo(() => {
    return {
      input: {
        key: "in",
        type: "target",
        required: true,
        connected: edges?.find((edge) => edge.target === node.id),
        source_type: ["root", "agent", "chain", "flow"],
      },
      default: {
        key: "default",
        type: "source",
        // TODO: use runnable types constant
        source_type: ["agent", "chain", "flow"],
        required: false,
        connected: edges?.find(
          (edge) => edge.source === node.id && edge.sourceHandle === "default"
        ),
      },
      branches: node?.config?.branches_hash?.map((branchKey, i) => ({
        key: branchKey,
        label: node?.config?.branches[i],
        type: "source",
        source_type: ["agent", "chain", "flow"],
        required: true,
        connected: edges?.find(
          (edge) => edge.source === node.id && edge.sourceHandle === branchKey
        ),
      })),
    };
  }, [edges, node.id, node?.config?.branches]);
};

export const InputConnector = ({
  type,
  node,
  required = true,
  id = "in",
  label = "Input",
}) => {
  const connector = useFlowConnectors(node)[id];
  const inputColor = useConnectorColor(node, connector);
  return (
    <Box position="relative">
      <Handle
        id={id}
        type="target"
        position="left"
        style={{ top: "50%", transform: "translateY(-50%)" }}
      />
      <Heading fontSize="xs" px={2} color={inputColor}>
        <ConnectorPopover
          type={type}
          node={node}
          connector={connector}
          label={label}
          placement={"left"}
        />{" "}
        {required && <RequiredAsterisk color={inputColor} />}
      </Heading>
    </Box>
  );
};

export const DefaultConnector = ({ type, node }) => {
  const { default: defaultNode } = useFlowConnectors(node);
  const outputColor = useConnectorColor(node, defaultNode);
  return (
    <Box position="relative">
      <Handle
        id="out"
        type="source"
        position="right"
        style={{ top: "50%", transform: "translateY(-50%)" }}
      />
      <Heading fontSize="xs" px={2} color={outputColor}>
        <ConnectorPopover
          type={type}
          node={node}
          connector={defaultNode}
          label={"Default"}
          placement={"right"}
        />
      </Heading>
    </Box>
  );
};

export const BranchTarget = ({ node, connector }) => {
  const color = useConnectorColor(node, connector);

  return (
    <Box position="relative" width="100%">
      <Handle id={connector.key} type="source" position={"right"} />
      <Box px={2} m={0} color={color}>
        <ConnectorPopover
          type={null}
          node={node}
          connector={connector}
          placement={"right"}
        />{" "}
        {connector.required && <RequiredAsterisk color={color} />}
      </Box>
    </Box>
  );
};

export const BranchConnectors = ({ node }) => {
  const { branches } = useFlowConnectors(node);

  return (
    <Flex justify={"space-between"}>
      <VStack spacing={0} cursor="default"></VStack>
      <VStack>
        {branches?.map((connector, i) => (
          <BranchTarget key={connector.key} node={node} connector={connector} />
        ))}
      </VStack>
    </Flex>
  );
};

export const BranchNode = ({ type, node, config, onFieldChange }) => {
  return (
    <VStack spacing={0} alignItems="stretch" fontSize="xs">
      <Flex mt={1} mb={3} justify={"space-between"}>
        <InputConnector type={type} node={node} />
        <DefaultConnector type={type} node={node} />
      </Flex>
      <BranchConnectors node={node} />
    </VStack>
  );
};
