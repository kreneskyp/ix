import React, { useContext } from "react";
import { Box, Tab, TabPanel, Tooltip } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faComments,
  faNetworkWired,
  faRobot,
} from "@fortawesome/free-solid-svg-icons";
import { ConfigEditorPane } from "chains/editor/ConfigEditorPane";
import { ChainEditorPane } from "chains/editor/ChainEditorPane";
import { TestChatPane } from "chains/editor/TestChatPane";
import { SelectedNodeContext } from "chains/editor/contexts";
import {
  SidebarTabList,
  SidebarTabPanels,
  SidebarTabs,
} from "site/SidebarTabs";
import Sidebar from "site/sidebar/Sidebar";

export const EditorRightSidebar = () => {
  // Tabs state
  const [tabIndex, setTabIndex] = React.useState(1);

  // Select node config pane on node select
  const { selectedNode } = useContext(SelectedNodeContext);
  React.useEffect(() => {
    if (selectedNode) {
      // default to chain config pane
      setTabIndex(0);
    }
  }, [selectedNode]);

  return (
    <Sidebar position={"right"}>
      <SidebarTabs index={tabIndex} onChange={setTabIndex}>
        <SidebarTabList>
          <Tooltip label="Node" aria-label="Node">
            <Tab>
              <FontAwesomeIcon icon={faNetworkWired} />
            </Tab>
          </Tooltip>
          <Tooltip label="Agent" aria-label="Agent">
            <Tab>
              <FontAwesomeIcon icon={faRobot} />
            </Tab>
          </Tooltip>
          <Tooltip label="Chat" aria-label="Chat">
            <Tab>
              <FontAwesomeIcon icon={faComments} />
            </Tab>
          </Tooltip>
        </SidebarTabList>
        <SidebarTabPanels>
          <TabPanel p={0}>
            <ConfigEditorPane />
          </TabPanel>
          <TabPanel p={3}>
            <ChainEditorPane />
          </TabPanel>
          <TabPanel
            p={0}
            m={0}
            display="flex"
            flex="1"
            flexDirection="column"
            justifyContent="flex-end"
            height={"calc(100vh)"}
          >
            <TestChatPane />
          </TabPanel>
          <TabPanel>
            <p>Validation content here</p>
          </TabPanel>
          <TabPanel>
            <p>Assistant content here</p>
          </TabPanel>
        </SidebarTabPanels>
      </SidebarTabs>
    </Sidebar>
  );
};
