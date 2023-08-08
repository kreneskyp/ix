import React from "react";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { Box, Heading, Spinner, VStack } from "@chakra-ui/react";
import { NewAgentButton } from "agents/NewAgentButton";
import { AgentEditor } from "agents/AgentEditor";
import { useParams } from "react-router-dom";
import { useDetailAPI } from "utils/hooks/useDetailAPI";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { useObjectEditorView } from "utils/hooks/useObjectEditorView";

export const useChains = () => {
  return usePaginatedAPI("/api/chains/", { limit: 1000 });
};

export const AgentEditorView = () => {
  const { id } = useParams();
  const {
    data: agent,
    load,
    error: agentError,
  } = useDetailAPI(`/api/agents/${id}`, { load: false });
  const { page: chainsPage, error: chainsError } = useChains();
  const chains = chainsPage?.objects;
  const { isNew, idRef } = useObjectEditorView(id, load);

  let content;
  if (!chains) {
    content = <Spinner />;
  } else if (isNew) {
    content = <AgentEditor key={idRef} chains={chains} />;
  } else if (!agent) {
    content = <Spinner />;
  } else {
    content = <AgentEditor agent={agent} chains={chains} />;
  }

  return (
    <Layout>
      <LayoutLeftPane>
        <NewAgentButton />
      </LayoutLeftPane>
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          <Heading>Agents</Heading>
          <Box width={500}>{content}</Box>
        </VStack>
      </LayoutContent>
    </Layout>
  );
};

AgentEditorView.defaultProps = {
  agentId: null,
};
