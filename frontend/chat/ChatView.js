import React, { useEffect } from "react";
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

export const ChatLeftPaneShim = ({ graph, loadGraph }) => {
  return (
    <>
      <ChatAssistantsButton graph={graph} />
      <ChatMembersButton graph={graph} loadGraph={loadGraph} />
    </>
  );
};

export const ChatRightSidebar = ({ graph, disclosure }) => {
  return (
    <RightSidebar {...disclosure}>
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
          <HStack justifyContent={"start"}>
            <Box
              width="100%"
              height="100vh"
              display="flex"
              flexDirection="column"
            >
              <ChatInterface graph={graph} />
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
            />
          </HStack>
        )}
      </LayoutContent>
    </Layout>
  );
};
