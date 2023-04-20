import React, { useState } from "react";
import {
  Box,
  Button,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  useToast,
} from "@chakra-ui/react";
import { AgentCommandsEditor } from "agents/AgentCommandsEditor";
import { AgentPromptEditor } from "agents/AgentPromptEditor";
import { AgentGeneralEditor } from "agents/AgentGeneralEditor";
import { AgentMetricsPanel } from "agents/AgentMetricsPanel";
import { useMutation } from "react-relay/hooks";
import { UpdateAgentMutation } from "agents/graphql/AgentMutations";

export const AgentEditor = ({ agent }) => {
  const [commit] = useMutation(UpdateAgentMutation);
  const [agentData, setAgentData] = useState(
    agent || {
      name: "",
      purpose: "",
      model: "",
      systemPrompt: "",
      commands: "[]",
      config: {},
    }
  );
  const toast = useToast();

  const updateAgent = () => {
    const input = {
      ...agentData,
      config: agentData.config,
    };
    commit({
      variables: { input },
      onCompleted: () => {
        toast({
          title: "Saved",
          description: "Saved agent.",
          status: "success",
          duration: 3000,
          isClosable: true,
        });
      },
      onError: (e) => {
        toast({
          title: "Error",
          description: `Failed to save the agent: ${e}`,
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      },
    });
  };

  return (
    <Box>
      <Tabs>
        <TabList>
          <Tab>Agent</Tab>
          <Tab>Prompt</Tab>
          <Tab>Commands</Tab>
          <Tab>Resources</Tab>
          <Tab>Metrics</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            <AgentGeneralEditor
              agentData={agentData}
              setAgentData={setAgentData}
            />
          </TabPanel>
          <TabPanel>
            <AgentPromptEditor
              agentData={agentData}
              setAgentData={setAgentData}
            />
          </TabPanel>
          <TabPanel>
            <AgentCommandsEditor
              agentData={agentData}
              setAgentData={setAgentData}
            />
          </TabPanel>
          <TabPanel>
            <AgentMetricsPanel agent={agent} />
          </TabPanel>
        </TabPanels>
      </Tabs>
      <Box width="100%" justify="right">
        <Button colorScheme="green" onClick={updateAgent}>
          Save
        </Button>
      </Box>
    </Box>
  );
};
