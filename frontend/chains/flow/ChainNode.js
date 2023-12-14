import React, { useMemo } from "react";
import { Handle, useEdges } from "reactflow";
import { Box, VStack, Heading, Flex } from "@chakra-ui/react";
import { NodeProperties, useConnectorColor } from "chains/flow/ConfigNode";
import { RequiredAsterisk } from "components/RequiredAsterisk";
import { ConnectorPopover } from "chains/editor/ConnectorPopover";

const useFlowConnectors = (node) => {
  const edges = useEdges();
  return useMemo(() => {
    // flow connectors for chains/runnables are always in/out
    return {
      input: {
        key: "in",
        type: "target",
        required: true,
        connected: edges?.find((edge) => edge.target === node.id),
        source_type: ["root", "agent", "chain"],
      },
      output: {
        key: "out",
        type: "source",
        // TODO: need to handle agent/chain output types
        //       reusing source_types property for now since
        //       the rest of the code is treated the same.
        source_type: ["agent", "chain"],
        required: false,
        connected: edges?.find((edge) => edge.source === node.id),
      },
    };
  }, [edges, node.id]);
};

export const InputConnector = ({ type, node }) => {
  const { input } = useFlowConnectors(node);
  const intputColor = useConnectorColor(node, input);

  return (
    <Box position="relative">
      <Handle
        id="in"
        type="target"
        position="left"
        style={{ top: "50%", transform: "translateY(-50%)" }}
      />
      <Heading fontSize="xs" px={2} color={intputColor}>
        <ConnectorPopover
          type={type}
          node={node}
          connector={input}
          label={"Input"}
          placement={"left"}
        />{" "}
        <RequiredAsterisk color={intputColor} />
      </Heading>
    </Box>
  );
};

export const OutputConnector = ({ type, node }) => {
  const { output } = useFlowConnectors(node);
  const outputColor = useConnectorColor(node, output);
  const outputConnector = type.connectors?.find((c) => c.key === "out");

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
          label={outputConnector?.label || "Output"}
          placement={"right"}
        />
      </Heading>
    </Box>
  );
};

export const ChainNode = ({ type, node, config, onFieldChange }) => {
  return (
    <VStack spacing={0} alignItems="stretch" fontSize="xs">
      <Flex mt={1} mb={3} justify={"space-between"}>
        <InputConnector type={type} node={node} />
        <OutputConnector type={type} node={node} />
      </Flex>
      <NodeProperties node={node} type={type} />
    </VStack>
  );
};
