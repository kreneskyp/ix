import { TabList, TabPanels, Tabs } from "@chakra-ui/react";
import React from "react";
import { useColorMode } from "@chakra-ui/color-mode";

const DARK = {
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
const LIGHT = {
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

export const useSidebarColorMode = () => {
  return useColorMode().colorMode === "dark" ? DARK : LIGHT;
};

export const SidebarTabList = ({ children, ...props }) => {
  const style = useSidebarColorMode();
  return (
    <TabList {...style.icon} {...props}>
      {children}
    </TabList>
  );
};

export const SidebarTabPanels = ({ children, ...props }) => {
  return (
    <TabPanels p={0} m={0} display="flex" flex="1" flexDirection="column">
      {children}
    </TabPanels>
  );
};

export const SidebarTabs = ({ children, ...props }) => {
  return (
    <Tabs
      isLazy
      isFitted
      m={0}
      p={0}
      pt={2}
      flex="1"
      flexDirection="column"
      display="flex"
      {...props}
    >
      {children}
    </Tabs>
  );
};
