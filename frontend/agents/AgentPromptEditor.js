import React, { useState } from "react";
import { Textarea, VStack } from "@chakra-ui/react";
import SliderInput from "components/SliderInput";

export const AgentPromptEditor = ({ agentData, setAgentData }) => {
  return (
    <VStack spacing={4} width="100%">
      <Textarea
        placeholder="Enter prompt text here"
        size="lg"
        minHeight="200px"
        resize="vertical"
        width="100%"
        fontSize={12}
        value={agentData?.systemPrompt || ""}
        onChange={(e) =>
          setAgentData({ ...agentData, systemPrompt: e.target.value })
        }
      />
    </VStack>
  );
};

export default AgentPromptEditor;
