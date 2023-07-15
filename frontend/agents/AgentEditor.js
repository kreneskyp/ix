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
import { useMutation, usePreloadedQuery } from "react-relay/hooks";
import { UpdateAgentMutation } from "agents/graphql/AgentMutations";
import { ChainsQuery } from "chains/graphql/ChainsQuery";
import { useNavigate, useParams } from "react-router-dom";

export const AgentEditor = ({ agent, chainsRef }) => {
  const { chains } = usePreloadedQuery(ChainsQuery, chainsRef);
  const [commit] = useMutation(UpdateAgentMutation);
  const { id } = useParams();

  // repack agent without data that can't be updated
  const { chain, createdAt, ...agentMinusChain } = agent || {};
  const initialData = { ...agentMinusChain, chainId: chain?.id };

  const [agentData, setAgentData] = useState(initialData);
  const toast = useToast();
  const navigate = useNavigate();

  const updateAgent = () => {
    const input = {
      ...agentData,
      id: id,
      config: agentData.config,
    };
    commit({
      variables: { input },
      onCompleted: (response) => {
        if (id === undefined) {
          navigate(`/agents/${response.updateAgent.agent.id}`, {});
        }
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
