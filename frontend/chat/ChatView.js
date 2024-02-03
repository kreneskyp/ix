import React, { useCallback, useEffect } from "react";
import { useParams } from "react-router-dom";
import {
  Spinner,
  Box,
  HStack,
  useDisclosure,
  IconButton,
} from "@chakra-ui/react";

import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { RightSidebar } from "site/RightSidebar";
import SideBarArtifactList from "chat/sidebar/SideBarArtifactList";
import { ChatInterface } from "chat/ChatInterface";
import { useChatGraph } from "chat/hooks/useChatGraph";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRightLeft } from "@fortawesome/free-solid-svg-icons";
import { ChatMembersButton } from "chat/buttons/ChatMembersButton";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { useLinkedScroll } from "hooks/useLinkedScroll";
import { ChatGraph, ChatAgents } from "chat/contexts";
import { AgentCardListButton } from "agents/AgentCardListButton";
import { ChatAgentCard } from "chat/agents/ChatAgentCard";
import { ChatInputProvider } from "chat/input/ChatInputProvider";

export const ChatLeftPaneShim = ({ graph }) => {
  const chatAgentsAPI = usePaginatedAPI(`/api/agents/`, {
    limit: 10000,
    load: false,
  });
  const queryArgs = { chat_id: graph.chat.id };
  const onUpdateAgents = useCallback(() => {
    chatAgentsAPI.load(queryArgs);
  }, [chatAgentsAPI.load]);

  // force refresh on chat.id change
  useEffect(() => {
    chatAgentsAPI.load(queryArgs);
  }, [chatAgentsAPI.load, graph.chat.id]);

  return (
    <ChatGraph.Provider value={graph}>
      <ChatAgents.Provider value={chatAgentsAPI}>
        <AgentCardListButton Card={ChatAgentCard} />
        <ChatMembersButton
          graph={graph}
          onUpdateAgents={onUpdateAgents}
          agentPage={chatAgentsAPI.page}
        />
      </ChatAgents.Provider>
    </ChatGraph.Provider>
  );
};

export const ChatRightSidebar = ({ graph, disclosure, drawerRef }) => {
  return (
    <RightSidebar {...disclosure} drawerRef={drawerRef}>
      <Box p={5} m={0} display="flex" flex="1" flexDirection="column">
        <SideBarArtifactList chat={graph.chat} artifacts={graph.artifacts} />
      </Box>
    </RightSidebar>
  );
};

export const ChatViewProvider = ({ children }) => {
  return <ChatInputProvider>{children}</ChatInputProvider>;
};

export const ChatView = () => {
  const { id } = useParams();
  const { response, call: loadGraph, isLoading } = useChatGraph(id);
  const graph = response?.data;
  const rightSidebarDisclosure = useDisclosure({ defaultIsOpen: true });
  const { targetRef: scrollBoxRef, sourceRef: drawerRef } = useLinkedScroll();

  useEffect(() => {
    loadGraph();
  }, [id]);

  return (
    <ChatViewProvider>
      <Layout>
        <LayoutLeftPane>
          {isLoading || !graph ? (
            <Spinner />
          ) : (
            <ChatLeftPaneShim graph={graph} />
          )}
        </LayoutLeftPane>
        <LayoutContent>
          {isLoading || !graph ? (
            <Spinner />
          ) : (
            <HStack justifyContent={"start"}>
              <Box
                width="100%"
                height="100vh"
                display="flex"
                flexDirection="column"
              >
                <ChatInterface
                  graph={graph}
                  scrollboxProps={{ ref: scrollBoxRef }}
                />
              </Box>
              <Box position="absolute" top={0} right={0} mt={4} mr={4}>
                <IconButton
                  ml="auto"
                  icon={<FontAwesomeIcon icon={faRightLeft} />}
                  onClick={rightSidebarDisclosure.onOpen}
                  aria-label="Open Sidebar"
                  title={"Open Sidebar"}
                />
              </Box>
              <ChatRightSidebar
                graph={graph}
                disclosure={rightSidebarDisclosure}
                drawerRef={drawerRef}
              />
            </HStack>
          )}
        </LayoutContent>
      </Layout>
    </ChatViewProvider>
  );
};
