import {
  Divider,
  FormControl,
  FormLabel,
  Input,
  Select,
  VStack,
} from "@chakra-ui/react";
import React from "react";
import { AGENT_MODELS } from "chains/constants";

export const AgentGeneralEditor = ({ agentData, setAgentData }) => {
  const ModelConfigForm = AGENT_MODELS[agentData?.model]?.configComponent;

  let modelConfigForm = null;
  if (ModelConfigForm !== undefined) {
    modelConfigForm = (
      <ModelConfigForm agent={agentData} setAgentData={setAgentData} />
    );
  }

  return (
    <VStack spacing={4}>
      <FormControl>
        <FormLabel>Model</FormLabel>
        <Select
          placeholder="Select AI model"
          value={agentData.model}
          mb={5}
          onChange={(e) =>
            setAgentData({ ...agentData, model: e.target.value })
          }
        >
          {Object.keys(AGENT_MODELS).map((key) => (
            <option key={key} value={key}>
              {AGENT_MODELS[key].name}
            </option>
          ))}
        </Select>
        <FormLabel>Agent Name</FormLabel>
        <Input
          placeholder="Model"
          value={agentData?.name || ""}
          mb={5}
          onChange={(e) => setAgentData({ ...agentData, name: e.target.value })}
        />
        <FormLabel>Purpose</FormLabel>
        <Input
          placeholder="Purpose"
          value={agentData?.purpose || ""}
          onChange={(e) =>
            setAgentData({ ...agentData, purpose: e.target.value })
          }
        />
        <Divider my={10} />
        {/* Model specific config */}
        {modelConfigForm}
      </FormControl>
    </VStack>
  );
};
