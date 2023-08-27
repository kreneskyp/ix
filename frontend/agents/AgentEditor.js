import React, { useState } from "react";
import {
  Box,
  Button,
  HStack,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  useToast,
} from "@chakra-ui/react";
import { AgentGeneralEditor } from "agents/AgentGeneralEditor";
import { AgentMetricsPanel } from "agents/AgentMetricsPanel";
import { useNavigate, useParams } from "react-router-dom";
import { useCreateUpdateAPI } from "utils/hooks/useCreateUpdateAPI";
import { APIErrorList } from "components/APIErrorList";

export const AgentEditor = ({ agent, chains }) => {
  const { id } = useParams();
  const [agentData, setAgentData] = useState(agent || {});

  const { save, isLoading } = useCreateUpdateAPI(
    "/api/agents/",
    `/api/agents/${id}`
  );

  const toast = useToast();
  const navigate = useNavigate();

  const updateAgent = async () => {
    try {
      const updatedAgent = await save(agentData);
      if (id === undefined) {
        navigate(`/agents/${updatedAgent.id}`, {});
      }
      toast({
        title: "Saved",
        description: "Saved agent.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: <APIErrorList error={error} />,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Box>
      <Tabs>
        <TabList>
          <Tab>Agent</Tab>
          <Tab>Resources</Tab>
          <Tab>Metrics</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            <AgentGeneralEditor
              agentData={agentData}
              setAgentData={setAgentData}
              chains={chains}
            />
          </TabPanel>
          <TabPanel>
            <AgentMetricsPanel agent={agent} />
          </TabPanel>
        </TabPanels>
      </Tabs>
      <HStack width="100%" justify="right" mt={5} mb={5}>
        <Button colorScheme="green" onClick={updateAgent}>
          Save
        </Button>
      </HStack>
    </Box>
  );
};
