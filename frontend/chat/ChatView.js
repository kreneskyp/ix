import React, { useCallback, useEffect } from "react";
import { useParams } from "react-router-dom";
import {
  Spinner,
  Box,
  HStack,
  useDisclosure,
  Tab,
  Tooltip,
  TabPanel,
  TabPanels,
  IconButton,
} from "@chakra-ui/react";

import { Layout, LayoutContent, LayoutLeftPane } from "site/Layout";
import { RightSidebar } from "site/RightSidebar";
import SideBarPlanList from "chat/SideBarPlanList";
import SideBarArtifactList from "chat/sidebar/SideBarArtifactList";
import { ChatInterface } from "chat/ChatInterface";
import { useChatGraph } from "chat/hooks/useChatGraph";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBox,
  faClipboardCheck,
  faRightLeft,
} from "@fortawesome/free-solid-svg-icons";
import { SidebarTabList, SidebarTabs } from "site/SidebarTabs";
import { ChatMembersButton } from "chat/ChatMembersButton";
import { ChatAssistantsButton } from "chat/ChatAssistantsButton";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { useLinkedScroll } from "hooks/useLinkedScroll";

export const ChatLeftPaneShim = ({ graph }) => {
  const { load: loadAgents, page: agentPage } = usePaginatedAPI(
    `/api/agents/`,
    { limit: 10000, load: false }
  );
  const queryArgs = { chat_id: graph.chat.id };
  const onUpdateAgents = useCallback(() => {
    loadAgents(queryArgs);
  }, [loadAgents]);

  // force refresh on chat.id change
  useEffect(() => {
    loadAgents(queryArgs);
  }, [loadAgents, graph.chat.id]);

  return (
    <>
      <ChatAssistantsButton
        graph={graph}
        onUpdateAgents={onUpdateAgents}
        agentPage={agentPage}
      />
      <ChatMembersButton
        graph={graph}
        onUpdateAgents={onUpdateAgents}
        agentPage={agentPage}
      />
    </>
  );
};

export const ChatRightSidebar = ({ graph, disclosure, onWheel, drawerRef }) => {
  return (
    <RightSidebar
      {...disclosure}
      onWheel={onWheel}
      drawerRef={drawerRef}
      pointerEvents={"auto"}
    >
      <SidebarTabs>
        <SidebarTabList>
          <Tooltip label="Tasks" aria-label="Tasks">
            <Tab>
              <FontAwesomeIcon icon={faClipboardCheck} />
            </Tab>
          </Tooltip>
          <Tooltip label="Artifacts" aria-label="Artifacts">
            <Tab>
              <FontAwesomeIcon icon={faBox} />
            </Tab>
          </Tooltip>
        </SidebarTabList>
        <TabPanels p={0} m={0} display="flex" flex="1" flexDirection="column">
          <TabPanel>
            <SideBarPlanList plans={graph.plans} />
          </TabPanel>
          <TabPanel>
            <SideBarArtifactList
              chat={graph.chat}
              artifacts={graph.artifacts}
            />
          </TabPanel>
        </TabPanels>
      </SidebarTabs>
    </RightSidebar>
  );
};

export const ChatView = () => {
  const { id } = useParams();
  const { response, call: loadGraph, isLoading } = useChatGraph(id);
  const graph = response?.data;
  const rightSidebarDisclosure = useDisclosure({ defaultIsOpen: true });
  const {
    updateScroll,
    targetRef: scrollBoxRef,
    sourceRef: drawerRef,
  } = useLinkedScroll();

  useEffect(() => {
    loadGraph();
  }, [id]);

  return (
    <Layout>
      <LayoutLeftPane>
        {isLoading || !graph ? <Spinner /> : <ChatLeftPaneShim graph={graph} />}
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
              onWheel={updateScroll}
              drawerRef={drawerRef}
            />
          </HStack>
        )}
      </LayoutContent>
    </Layout>
  );
};
