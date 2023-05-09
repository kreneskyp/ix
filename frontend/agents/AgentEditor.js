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

export const AgentEditor = ({ agent, chainsRef }) => {
  const { chains } = usePreloadedQuery(ChainsQuery, chainsRef);
  const [commit] = useMutation(UpdateAgentMutation);

  // repack agent without data that can't be updated
  const { chain, createdAt, ...agentMinusChain } = agent || {};
  const initialData = { ...agentMinusChain, chainId: chain?.id };

  const [agentData, setAgentData] = useState(initialData);
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
