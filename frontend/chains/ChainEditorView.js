import React, { useEffect, useState } from "react";
import { v4 as uuid4 } from "uuid";
import { usePreloadedQuery } from "react-relay/hooks";
import { useQueryLoader } from "react-relay";
import { useParams } from "react-router-dom";
import { Spinner, VStack } from "@chakra-ui/react";

import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { ChainGraphByIdQuery } from "chains/graphql/ChainGraphByIdQuery";
import ChainGraphEditor from "chains/ChainGraphEditor";
import { ChainGraphEditorSideBar } from "chains/editor/ChainGraphEditorSideBar";

const ChainEditorShim = ({ chainQueryRef }) => {
  const { graph } = usePreloadedQuery(ChainGraphByIdQuery, chainQueryRef);
  return <ChainGraphEditor graph={graph} />;
};

export const ChainEditorView = () => {
  const [chainQueryRef, loadChainQuery] = useQueryLoader(ChainGraphByIdQuery);
  const { id } = useParams();

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
      loadChainQuery({ id }, { fetchPolicy: "network-only" });
      setIdRef(id);
    } else {
      setIdRef(uuid4());
    }
  }, [isNew]);

  let content;
  if (isNew) {
    content = <ChainGraphEditor key={idRef} />;
  } else if (!chainQueryRef) {
    content = <Spinner />;
  } else {
    content = <ChainEditorShim chainQueryRef={chainQueryRef} />;
  }

  return (
    <Layout>
      <LayoutLeftPane>
        <ChainGraphEditorSideBar />
      </LayoutLeftPane>
      <LayoutContent>
        <VStack alignItems="start" p={5} spacing={4}>
          {content}
        </VStack>
      </LayoutContent>
    </Layout>
  );
};
