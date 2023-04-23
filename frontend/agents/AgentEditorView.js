import React, { useEffect } from "react";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { useQueryLoader } from "react-relay";
import { Heading, Spinner, VStack } from "@chakra-ui/react";
import { NewAgentButton } from "agents/NewAgentButton";
import { AgentEditor } from "agents/AgentEditor";
import { usePreloadedQuery } from "react-relay/hooks";
import { useParams } from "react-router-dom";
import { AgentByIdQuery } from "agents/graphql/AgentByIdQuery";

const AgentEditorShim = ({ queryRef }) => {
  const { agent } = usePreloadedQuery(AgentByIdQuery, queryRef);
  return <AgentEditor agent={agent} />;
};

export const AgentEditorView = () => {
  const { id } = useParams();
  let content;
  if (id !== undefined && id !== null) {
    const [queryRef, loadQuery] = useQueryLoader(AgentByIdQuery);

    useEffect(() => {
      loadQuery({ id }, { fetchPolicy: "network-only" });
    }, []);

    if (!queryRef) {
      content = <Spinner />;
    } else {
      content = <AgentEditorShim queryRef={queryRef} />;
    }
  } else {
    content = <AgentEditor agentId={id} />;
  }

  return (
    <Layout>
      <LayoutLeftPane>
        <NewAgentButton />
      </LayoutLeftPane>
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          <Heading>Agents</Heading>
          {content}
        </VStack>
      </LayoutContent>
    </Layout>
  );
};

AgentEditorView.defaultProps = {
  agentId: null,
};
