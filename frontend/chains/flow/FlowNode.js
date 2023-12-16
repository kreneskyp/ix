import React from "react";
import { Handle } from "reactflow";
import { Box, VStack, Heading, Flex } from "@chakra-ui/react";
import { useConnectorColor } from "chains/flow/ConfigNode";
import { RequiredAsterisk } from "components/RequiredAsterisk";
import { ConnectorPopover } from "chains/editor/ConnectorPopover";
import { useFlowConnectors } from "chains/flow/useFlowConnectors";

export const InputTarget = ({ node, connector }) => {
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
          connector={connector}
          label={"Input"}
          placement={"left"}
        />{" "}
        <RequiredAsterisk color={intputColor} />
      </Heading>
    </Box>
  );
};

export const InputsConnectors = ({ node }) => {
  const { inputs } = useFlowConnectors(node);

  return (
    <Flex justify={"space-between"}>
      <VStack spacing={0} cursor="default"></VStack>
      <VStack justifyContent="flex-start">
        {inputs?.map((connector, i) => (
          <InputTarget key={connector.key} node={node} connector={connector} />
        ))}
      </VStack>
    </Flex>
  );
};

export const OutputTarget = ({ node, connector }) => {
  const color = useConnectorColor(node, connector);

  return (
    <Box position="relative" width="100%">
      <Handle id={connector.key} type="source" position={"right"} />
      <Flex px={2} m={0} color={color} justifyContent="flex-end">
        <ConnectorPopover
          type={null}
          node={node}
          connector={connector}
          placement={"right"}
        />{" "}
        {connector.required && <RequiredAsterisk color={color} />}
      </Flex>
    </Box>
  );
};

export const OutputsConnectors = ({ node }) => {
  const { outputs } = useFlowConnectors(node);
  return (
    <Flex justify={"space-between"}>
      <VStack spacing={0} cursor="default"></VStack>
      <VStack justifyContent="flex-end">
        {outputs?.map((connector, i) => (
          <OutputTarget key={connector.key} node={node} connector={connector} />
        ))}
      </VStack>
    </Flex>
  );
};
