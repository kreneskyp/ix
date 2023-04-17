import React from "react";
import { Box, Tab, TabList, TabPanel, TabPanels, Tabs } from "@chakra-ui/react";
import { AgentCommandsEditor } from "agents/AgentCommandsEditor";
import { AgentPromptEditor } from "agents/AgentPromptEditor";
import { AgentGeneralEditor } from "agents/AgentGeneralEditor";
import { AgentMetricsPanel } from "agents/AgentMetricsPanel";

export const AgentEditor = ({ agent, agentData, setAgentData }) => {
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
    </Box>
  );
};
