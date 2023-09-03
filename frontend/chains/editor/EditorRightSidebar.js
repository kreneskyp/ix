import React, { useRef } from "react";
import {
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerOverlay,
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
  faRobot,
} from "@fortawesome/free-solid-svg-icons";
import { ConfigEditorPane } from "chains/editor/ConfigEditorPane";
import { ChainEditorPane } from "chains/editor/ChainEditorPane";

export const EditorRightSidebar = ({ isOpen, onOpen, onClose }) => {
  const btnRef = useRef();

  return (
    <div>
      <Drawer
        isOpen={isOpen}
        placement="right"
        onClose={onClose}
        finalFocusRef={btnRef}
        closeOnOverlayClick={false}
        trapFocus={false}
        size={"sm"}
      >
        <DrawerOverlay
          style={{ backgroundColor: "transparent", pointerEvents: "none" }}
        >
          <DrawerContent style={{ pointerEvents: "all" }}>
            <DrawerCloseButton />
            <DrawerBody>
              <Tabs isLazy>
                <TabList>
                  <Tooltip label="Node" aria-label="Node">
                    <Tab>
                      <FontAwesomeIcon icon={faNetworkWired} />
                    </Tab>
                  </Tooltip>
                  <Tooltip label="Chain" aria-label="Chain">
                    <Tab>
                      <FontAwesomeIcon icon={faChain} />
                    </Tab>
                  </Tooltip>
                </TabList>
                <TabPanels>
                  <TabPanel>
                    <ConfigEditorPane />
                  </TabPanel>
                  <TabPanel>
                    <ChainEditorPane />
                  </TabPanel>
                  <TabPanel>
                    <p>Chat content here</p>
                  </TabPanel>
                  <TabPanel>
                    <p>Validation content here</p>
                  </TabPanel>
                  <TabPanel>
                    <p>Assistant content here</p>
                  </TabPanel>
                </TabPanels>
              </Tabs>
            </DrawerBody>
          </DrawerContent>
        </DrawerOverlay>
      </Drawer>
    </div>
  );
};
