import React, { useContext, useRef } from "react";
import {
  Box,
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerOverlay,
  HStack,
  IconButton,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Tooltip,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faChain,
  faCheckCircle,
  faComments,
  faNetworkWired,
  faRightLeft,
  faRobot,
  faX,
} from "@fortawesome/free-solid-svg-icons";
import { ConfigEditorPane } from "chains/editor/ConfigEditorPane";
import { ChainEditorPane } from "chains/editor/ChainEditorPane";
import { ChatPane } from "chains/editor/ChatPane";
import { useColorMode } from "@chakra-ui/color-mode";
import { TestChatPane } from "chains/editor/TestChatPane";
import { useSelectedNode } from "chains/hooks/useSelectedNode";
import { SelectedNodeContext } from "chains/editor/contexts";

export const EditorRightSidebar = ({ isOpen, onOpen, onClose }) => {
  const btnRef = useRef();

  // drawer size state
  const [size, setSize] = React.useState("sm");
  const toggleSize = React.useCallback(() =>
    setSize((prev) => (prev === "sm" ? "xl" : "sm"))
  );

  // Tabs state
  const [tabIndex, setTabIndex] = React.useState(1);
  const handleTabsChange = React.useCallback((index) => setTabIndex(index));

  // Select node config pane on node select
  const { selectedNode } = useContext(SelectedNodeContext);
  React.useEffect(() => {
    if (selectedNode) {
      // default to chain config pane
      setTabIndex(0);
    }
  }, [selectedNode]);

  // style
  const dark = {
    header: {
      color: "gray.500",
    },
    headerContainer: {
      borderBottom: "1px solid",
      borderColor: "blackAlpha.100",
      bg: "blackAlpha.400",
    },
    icon: {
      color: "gray.500",
    },
  };
  const light = {
    header: {
      color: "gray.500",
    },
    headerContainer: {
      borderBottom: "1px solid",
      borderColor: "blackAlpha.200",
      bg: "blackAlpha.50",
    },
    icon: {
      color: "gray.400",
    },
  };
  const style = useColorMode().colorMode === "dark" ? dark : light;

  return (
    <Drawer
      isOpen={isOpen}
      placement="right"
      onClose={onClose}
      finalFocusRef={btnRef}
      closeOnOverlayClick={false}
      trapFocus={false}
      size={size}
    >
      <DrawerOverlay
        style={{ backgroundColor: "transparent", pointerEvents: "none" }}
      >
        <DrawerContent
          style={{ pointerEvents: "all" }}
          height="100vh"
          display="flex"
          flexDirection="column"
        >
          <DrawerHeader h={10} px={2} py={1} {...style.headerContainer}>
            <HStack display={"flex"} justifyContent={"flex-start"}>
              <IconButton
                aria-label="Expand"
                bg={"transparent"}
                icon={<FontAwesomeIcon icon={faRightLeft} />}
                size={"xs"}
                title={"Expanded"}
                onClick={toggleSize}
                {...style.header}
              />
              <IconButton
                aria-label={"Close"}
                bg={"transparent"}
                icon={<FontAwesomeIcon icon={faX} />}
                size={"xs"}
                title={"Close"}
                onClick={onClose}
                {...style.header}
              />
            </HStack>
          </DrawerHeader>
          <Tabs
            isLazy
            isFitted
            index={tabIndex}
            onChange={handleTabsChange}
            m={0}
            p={0}
            pt={2}
            flex="1"
            flexDirection="column"
            display="flex"
          >
            <TabList {...style.icon}>
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
            </TabList>
            <TabPanels
              p={0}
              m={0}
              display="flex"
              flex="1"
              flexDirection="column"
            >
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
              >
                <TestChatPane />
              </TabPanel>
              <TabPanel>
                <p>Validation content here</p>
              </TabPanel>
              <TabPanel>
                <p>Assistant content here</p>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </DrawerContent>
      </DrawerOverlay>
    </Drawer>
  );
};
