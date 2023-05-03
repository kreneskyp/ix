import React, { useEffect } from "react";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { useQueryLoader } from "react-relay";
import { Box, Heading, Spinner, VStack } from "@chakra-ui/react";
import { NewAgentButton } from "agents/NewAgentButton";
import { AgentEditor } from "agents/AgentEditor";
import { usePreloadedQuery } from "react-relay/hooks";
import { useParams } from "react-router-dom";
import { AgentByIdQuery } from "agents/graphql/AgentByIdQuery";
import {ChainsQuery} from "chains/graphql/ChainsQuery";

const AgentEditorShim = ({ queryRef, chainsRef }) => {
  const { agent } = usePreloadedQuery(AgentByIdQuery, queryRef);
  return <AgentEditor agent={agent} chainsRef={chainsRef} />;
};

export const AgentEditorView = () => {
  const [chainsRef, loadChains] = useQueryLoader(ChainsQuery);
  const { id } = useParams();
  let content;

  if (id !== undefined && id !== null) {
    const [queryRef, loadQuery] = useQueryLoader(AgentByIdQuery);

    useEffect(() => {
      loadChains();
      loadQuery({ id }, { fetchPolicy: "network-only" });
    }, []);

    if (!queryRef || !chainsRef) {
      content = <Spinner />;
    } else {
      content = <AgentEditorShim queryRef={queryRef} chainsRef={chainsRef} />;
    }
  } else {

    useEffect(() => {
      loadChains();
    }, []);

    if (!chainsRef) {
      content = <Spinner />;
    } else {
      content = <AgentEditor agentId={id} chainsRef={chainsRef}/>;
    }
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
