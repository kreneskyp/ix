import React from "react";
import { Box, Heading, VStack } from "@chakra-ui/react";
import CodeEditor from "components/code_editor/CodeEditor";

export const ExecutionDetail = ({ execution }) => {
  const formattedInputs =
    typeof execution?.inputs === "string"
      ? execution?.inputs
      : JSON.stringify(execution?.inputs, null, 4);
  const formattedOutputs =
    typeof execution?.outputs === "string"
      ? execution?.outputs
      : JSON.stringify(execution?.outputs, null, 4);

  return (
    <Box pl={4} pt={1} height={"100%"}>
      <VStack alignItems={"start"} spacing={3}>
        <Box width={"100%"}>
          <Heading size={"sm"} mb={1}>
            Input
          </Heading>
          <Box mr={10}>
            <CodeEditor
              key={execution?.id}
              language="json"
              value={formattedInputs}
            />
          </Box>
        </Box>
        <Box width={"100%"}>
          <Heading size={"sm"} mb={1}>
            Output
          </Heading>
          <Box mr={10}>
            <CodeEditor
              key={execution?.id}
              language="json"
              value={formattedOutputs}
            />
          </Box>
        </Box>
        {execution?.message && (
          <Box width={"100%"}>
            <Heading size={"sm"} mb={1}>
              Message
            </Heading>
            <Box mr={10}>
              <CodeEditor
                key={execution?.id}
                language="json"
                value={execution?.message || "<no message>"}
              />
            </Box>
          </Box>
        )}
      </VStack>
    </Box>
  );
};
