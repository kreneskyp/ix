import {
  Divider,
  FormControl,
  FormLabel,
  Input,
  Select,
  Box,
  VStack,
} from "@chakra-ui/react";
import React from "react";
import { AGENT_MODELS } from "chains/constants";

export const AgentGeneralEditor = ({ agentData, setAgentData, chains }) => {
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
        <FormLabel>Agent Name</FormLabel>
        <Input
          placeholder="Model"
          value={agentData?.name || ""}
          p={5}
          onChange={(e) => setAgentData({ ...agentData, name: e.target.value })}
        />
        <FormLabel>Alias (chat tag)</FormLabel>
        <Input
          placeholder="alias"
          value={agentData?.alias || ""}
          p={5}
          onChange={(e) =>
            setAgentData({ ...agentData, alias: e.target.value })
          }
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
        <FormLabel>Chain</FormLabel>
        <Box p={5} my={5} bg="blackAlpha.300">
          The agent's chain is called in response to inputs. The chain defines
          the behavior and capabilities of the agent.
        </Box>
        <Select
          placeholder="Select chain"
          value={agentData.chain_id}
          mb={5}
          onChange={(e) =>
            setAgentData({ ...agentData, chain_id: e.target.value })
          }
        >
          {chains.map((chain) => (
            <option key={chain.id} value={chain.id}>
              {chain.name}
            </option>
          ))}
        </Select>

        <Divider my={10} />
        <FormLabel>Default Model</FormLabel>
        <Box p={5} my={5} bg="blackAlpha.300">
          The default model will be used by the chain when it does not specify a
          model. Steps in a chain may override this with a specific model or
          configuration.
        </Box>
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

        {/* Model specific config */}
        {modelConfigForm}
      </FormControl>
    </VStack>
  );
};
