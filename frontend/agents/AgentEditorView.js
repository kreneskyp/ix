import React, { useEffect, useState } from "react";
import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { useQueryLoader } from "react-relay";
import { Box, Heading, Spinner, VStack } from "@chakra-ui/react";
import { NewAgentButton } from "agents/NewAgentButton";
import { AgentEditor } from "agents/AgentEditor";
import { usePreloadedQuery } from "react-relay/hooks";
import { useParams } from "react-router-dom";
import { AgentByIdQuery } from "agents/graphql/AgentByIdQuery";
import { ChainsQuery } from "chains/graphql/ChainsQuery";
import { v4 as uuid4 } from "uuid";

const AgentEditorShim = ({ queryRef, chainsRef }) => {
  const { agent } = usePreloadedQuery(AgentByIdQuery, queryRef);
  return <AgentEditor agent={agent} chainsRef={chainsRef} />;
};

export const AgentEditorView = () => {
  const [chainsRef, loadChains] = useQueryLoader(ChainsQuery);
  const [agentQueryRef, loadAgentQuery] = useQueryLoader(AgentByIdQuery);
  const { id } = useParams();

  useEffect(() => {
    loadChains({}, { fetchPolicy: "network-only" });
  }, []);

  // state for handling whether how to load the data (new vs existing)
  // and when to reset the editor when opened. The cached state does not
  // reset when the url changes as protection against reloading when
  // creating new chains. This state tracks when to reset the cache.
  const [idRef, setIdRef] = useState(null);
  const [isNew, setIsNew] = useState(null);
  const [wasCreated, setWasCreated] = useState(null);
  useEffect(() => {
    const firstRender = isNew === null;
    if (firstRender) {
      // first render caches whether this started as a new chain
      setIsNew(id === undefined);
    } else {
      // switch from existing to new
      if (id === undefined && !isNew) {
        setIsNew(true);
        setWasCreated(false);
      }
      // a new chain was created
      if (id !== undefined && isNew) {
        setWasCreated(true);
      }
      // switch from created to new
      if (id === undefined && wasCreated) {
        setIsNew(true);
        setWasCreated(false);
        setIdRef(uuid4());
      }
    }
  }, [id]);

  useEffect(() => {
    // load chain if id is provided on view load
    // otherwise state will be handled internally by the editor
    if (isNew === false) {
      loadAgentQuery({ id }, { fetchPolicy: "network-only" });
      setIdRef(id);
    } else {
      setIdRef(uuid4());
    }
  }, [isNew]);

  let content;
  if (!chainsRef) {
    content = <Spinner />;
  } else if (isNew) {
    content = <AgentEditor key={idRef} chainsRef={chainsRef} />;
  } else if (!agentQueryRef) {
    content = <Spinner />;
  } else {
    content = (
      <AgentEditorShim queryRef={agentQueryRef} chainsRef={chainsRef} />
    );
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
