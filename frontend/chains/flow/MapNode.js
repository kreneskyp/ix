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
      output: {
        key: "out",
        type: "source",
        source_type: ["agent", "chain", "flow", "chain-link"],
        required: false,
        connected: edges?.find((edge) => edge.source === node.id),
      },
      steps: node?.config?.steps_hash?.map((mapKey, i) => ({
        key: mapKey,
        label: node?.config?.steps[i],
        type: "target",
        source_type: ["agent", "chain", "tool", "retriever", "flow"],
        required: true,
        connected: edges?.find(
          (edge) => edge.target === node.id && edge.targetHandle === mapKey
        ),
      })),
    };
  }, [edges, node.id, node?.config?.steps]);
};

export const OutputConnector = ({ type, node }) => {
  const { output } = useFlowConnectors(node);
  const outputColor = useConnectorColor(node, output);
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
          connector={output}
          label={"Output"}
          placement={"right"}
        />
      </Heading>
    </Box>
  );
};

export const MapTarget = ({ node, connector }) => {
  const color = useConnectorColor(node, connector);

  return (
    <Box position="relative" width="100%">
      <Handle id={connector.key} type="target" position={"left"} />
      <Box px={2} m={0} color={color}>
        <ConnectorPopover
          type={null}
          node={node}
          connector={connector}
          placement={"left"}
        />{" "}
        {connector.required && <RequiredAsterisk color={color} />}
      </Box>
    </Box>
  );
};

export const MapConnectors = ({ node }) => {
  const { steps } = useFlowConnectors(node);

  return (
    <Flex justify={"space-between"}>
      <VStack>
        {steps?.map((connector, i) => (
          <MapTarget key={connector.key} node={node} connector={connector} />
        ))}
      </VStack>
      <Box />
    </Flex>
  );
};

export const MapNode = ({ type, node, config, onFieldChange }) => {
  return (
    <VStack spacing={0} alignItems="stretch" fontSize="xs">
      <Flex mt={1} mb={3} justify={"space-between"}>
        <Box />
        <OutputConnector type={type} node={node} />
      </Flex>
      <MapConnectors node={node} />
    </VStack>
  );
};
