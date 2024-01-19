import React from "react";

import { Box, Flex, Tab, TabPanel, Tooltip } from "@chakra-ui/react";

import {
  SidebarTabList,
  SidebarTabPanels,
  SidebarTabs,
} from "site/SidebarTabs";
import SchemaDefsList from "schemas/openapi/SchemaDefsList";
import SchemaPathsList from "schemas/openapi/SchemaPathsList";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const OpenAPIFormRightPanel = ({ schema }) => {
  const [tabIndex, setTabIndex] = React.useState(0);
  const { scrollbar } = useEditorColorMode();

  return (
    <Flex w={"100%"} h={"100%"} display={"flex"} alignItems={"start"}>
      <SidebarTabs index={tabIndex} onChange={setTabIndex}>
        <SidebarTabList>
          <Tooltip label="Paths" aria-label="Paths">
            <Tab>Paths</Tab>
          </Tooltip>
          <Tooltip label="Schemas" aria-label="Schemas">
            <Tab>Schemas</Tab>
          </Tooltip>
        </SidebarTabList>
        <SidebarTabPanels>
          <TabPanel>
            <Box
              height="400px"
              overflowY="auto"
              css={scrollbar}
              width={"100%"}
              pr={4}
            >
              {schema?.value?.paths && (
                <Box width={"100%"}>
                  <SchemaPathsList schema={schema.value} />
                </Box>
              )}
            </Box>
          </TabPanel>
          <TabPanel>
            <Box
              height="400px"
              overflowY="auto"
              css={scrollbar}
              width={"100%"}
              pr={4}
            >
              {schema?.value?.components && (
                <SchemaDefsList schema={schema.value} />
              )}
            </Box>
          </TabPanel>
        </SidebarTabPanels>
      </SidebarTabs>
    </Flex>
  );
};
