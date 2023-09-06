import React, { Suspense, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Spinner, VStack, Box } from "@chakra-ui/react";

import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import SideBarPlanList from "chat/SideBarPlanList";
import SideBarArtifactList from "chat/sidebar/SideBarArtifactList";
import SideBarAgentList from "chat/sidebar/SideBarAgentList";
import { ChatInterface } from "chat/ChatInterface";
import { useChatGraph } from "chat/hooks/useChatGraph";
import { NewAgentButton } from "agents/NewAgentButton";

export const ChatLeftPaneShim = ({ graph, loadGraph }) => {
  return (
    <>
      <NewAgentButton />
      <Suspense>
        <VStack spacing={4} align="stretch">
          <SideBarAgentList graph={graph} loadGraph={loadGraph} />
          <SideBarPlanList plans={graph.plans} />
          <SideBarArtifactList chat={graph.chat} artifacts={graph.artifacts} />
        </VStack>
      </Suspense>
    </>
  );
};

export const ChatView = () => {
  const { id } = useParams();
  const { response, call: loadGraph, isLoading } = useChatGraph(id);
  const graph = response?.data;

  useEffect(() => {
    loadGraph();
  }, [id]);

  return (
    <Layout>
      <LayoutLeftPane>
        {isLoading || !graph ? (
          <Spinner />
        ) : (
          <ChatLeftPaneShim graph={graph} loadGraph={loadGraph} />
        )}
      </LayoutLeftPane>
      <LayoutContent>
        {isLoading || !graph ? (
          <Spinner />
        ) : (
          <Box height="100%" display="flex" flexDirection="column">
            <ChatInterface graph={graph} />
          </Box>
        )}
      </LayoutContent>
    </Layout>
  );
};
