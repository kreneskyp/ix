import React, {useMemo} from "react";
import { Handle, useEdges } from "reactflow";
import { Box, VStack, Heading, Flex } from "@chakra-ui/react";
import { TypeAutoFields } from "chains/flow/TypeAutoFields";
import { CollapsibleSection } from "chains/flow/CollapsibleSection";
import {NodeProperties, useConnectorColor} from "chains/flow/ConfigNode";
import {RequiredAsterisk} from "components/RequiredAsterisk";


const useFlowConnectors = (node) => {
  const edges = useEdges();
  return useMemo(() => {
    // flow connectors for chains/runnables are always in/out
    return {
      input: {
        key: "in",
        required: true,
        connected: edges?.find((edge) => edge.target === node.id)
      },
      output: {
        key: "out",
        required: false,
        connected: edges?.find((edge) => edge.source === node.id)
      }
    }
  }, [edges, node.id]);
};


export const ChainNode = ({ type, node, config, onFieldChange }) => {
  const { input, output } = useFlowConnectors(node);
  const intputColor = useConnectorColor(input);
  const outputColor = useConnectorColor(output);

  return (
    <VStack spacing={0} alignItems="stretch" fontSize="xs">
      <Flex mt={1} mb={3} justify={"space-between"}>
        <Box position="relative">
          <Handle
            id="in"
            type="target"
            position="left"
            style={{ top: "50%", transform: "translateY(-50%)" }}
          />
          <Heading fontSize="xs" px={2} color={intputColor} >
            Inputs <RequiredAsterisk color={intputColor} />
          </Heading>
        </Box>

        <Box position="relative">
          <Handle
            id="out"
            type="source"
            position="right"
            style={{ top: "50%", transform: "translateY(-50%)" }}
          />
          <Heading fontSize="xs" px={2} color={outputColor}>
            Output
          </Heading>
        </Box>
      </Flex>
      <NodeProperties node={node} type={type} />
      <CollapsibleSection title="Config">
        <TypeAutoFields type={type} config={config} onChange={onFieldChange} />
      </CollapsibleSection>
    </VStack>
  );
};
