import React, { useCallback, useState } from "react";
import { Handle } from "reactflow";
import {
  Box,
  Heading,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMessage } from "@fortawesome/free-solid-svg-icons";
import PromptEditor from "chains/editor/PromptEditor";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const LLMNode = ({ data }) => {
  const config = data.config;
  const node = data.node;

  const [llmData, setLLMData] = useState(node?.config);
  const setData = useCallback(() => {}, []);

  const { border, color, highlight, highlightColor, bg } = useEditorColorMode();

  return (
    <Box
      borderWidth="0px"
      borderRadius={8}
      border="1px solid"
      borderColor={border}
      padding="0"
      backgroundColor={bg}
      width={500}
      color={color}
    >
      <Box position="relative">
        <Handle
          id="out"
          type="target"
          position="right"
          style={{ top: "50%", transform: "translateY(-50%)" }}
        />
        <Heading
          as="h4"
          size="xs"
          borderTopLeftRadius={7}
          borderTopRightRadius={7}
          color={highlightColor}
          bg={highlight.prompt}
          px={1}
          py={2}
        >
          <FontAwesomeIcon icon={faMessage} pr={3} /> Prompt
        </Heading>
      </Box>
      <Box p={3}>
        <PromptEditor />
      </Box>
    </Box>
  );
};

export default LLMNode;
