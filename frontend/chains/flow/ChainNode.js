import React from "react";
import { Handle } from "reactflow";
import { Box, VStack, Heading, Text, Divider, HStack } from "@chakra-ui/react";
import { llm_name } from "chains/utils";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { faChain } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

export const ChainNode = ({ data }) => {
  const node = data.node;
  const inputs = null;
  const outputs = null;

  const { border, color, highlight, highlightColor, bg } = useEditorColorMode();

  return (
    <Box
      borderWidth="0px"
      borderRadius={8}
      padding="0"
      border="1px solid"
      borderColor={border}
      backgroundColor={bg}
      width={250}
      color={color}
      boxShadow="md"
    >
      <Heading
        as="h4"
        size="xs"
        color={highlightColor}
        borderTopLeftRadius={7}
        borderTopRightRadius={7}
        bg={highlight.chain}
        px={1}
        py={2}
      >
        <FontAwesomeIcon icon={faChain} />{" "}
        {node.name || node.classPath.split(".").pop()}
      </Heading>
      <VStack spacing={0} alignItems="stretch">
        <Box>
          <strong>LLM: </strong>
          {llm_name(node.config?.llm?.class_path)}
        </Box>
        <Text pb={2}></Text>
        <Box position="relative">
          <Handle
            id="in"
            type="target"
            position="left"
            style={{ top: "50%", transform: "translateY(-50%)" }}
          />
          <Heading size="sm" px={2} bg="blackAlpha.200">
            Inputs
          </Heading>
        </Box>
        <VStack alignItems="stretch">
          {inputs?.map((input, index) => (
            <HStack key={index} spacing="2">
              <Text>{input}</Text>
            </HStack>
          ))}
        </VStack>
        <Box position="relative">
          <Handle
            id="out"
            type="source"
            position="right"
            style={{ top: "50%", transform: "translateY(-50%)" }}
          />
          <Heading size="sm" px={2} bg="blackAlpha.200">
            Output
          </Heading>
        </Box>
        <VStack alignItems="stretch" pb={2}>
          {outputs?.map((output, index) => (
            <HStack key={index} spacing="2">
              <Text>{output}</Text>
              <Handle type="source" position="bottom" id={`output-${index}`} />
            </HStack>
          ))}
        </VStack>
      </VStack>
    </Box>
  );
};

export default ChainNode;
