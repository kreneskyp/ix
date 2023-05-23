import React, { useCallback, useState } from "react";
import { Handle } from "reactflow";
import {
  Box,
  Heading,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBrain } from "@fortawesome/free-solid-svg-icons";
import { LLM_FORM_MAP } from "chains/editor/constants";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const LLMNode = ({ data }) => {
  const config = data.config;
  const node = data.node;

  const [llmData, setLLMData] = useState(node?.config);
  const setData = useCallback(() => {}, []);

  const { border, color, highlight, highlightColor, bg } = useEditorColorMode();

  const LLMForm = LLM_FORM_MAP[node.classPath];
  const options = config.options;
  let form = null;

  if (LLMForm !== undefined) {
    form = <LLMForm options={options} config={llmData} setData={setLLMData} />;
  }

  return (
    <Box
      borderWidth="0px"
      borderRadius={8}
      border="1px solid"
      borderColor={border}
      padding="0"
      color={color}
      backgroundColor={bg}
      width={250}
      boxShadow="md"
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
          color={highlightColor}
          bg={highlight.llm}
          borderTopLeftRadius={7}
          borderTopRightRadius={7}
          px={1}
          py={2}
        >
          <FontAwesomeIcon icon={faBrain} pr={3} /> {config.label}
        </Heading>
      </Box>
      <Box p={3}>{form}</Box>
    </Box>
  );
};

export default LLMNode;
