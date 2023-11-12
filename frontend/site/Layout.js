import React, { Suspense } from "react";
import { Divider, Flex, Spacer, VStack } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { ColorModeButton } from "components/ColorModeButton";
import { CenteredSpinner } from "site/CenteredSpinner";
import { NewChatButton } from "chat/buttons/NewChatButton";
import { NewAgentButton } from "agents/NewAgentButton";
import Navigation from "site/Navigation";
import SidebarProvider from "site/sidebar/context";

export const LayoutLeftPane = ({ children }) => {
  return children;
};

export const LayoutContent = ({ children }) => {
  return children;
};

export const Layout = ({ children }) => {
  const { colorMode } = useColorMode();

  const leftPane = React.Children.toArray(children).find(
    (child) => child.type === LayoutLeftPane
  );
  const content = React.Children.toArray(children).find(
    (child) => child.type === LayoutContent
  );

  return (
    <SidebarProvider>
      <Flex h="100vh" overflowX="hidden">
        <VStack
          bg={colorMode === "light" ? "gray.200" : "blackAlpha.200"}
          p={1}
          minH="100vh"
          align="left"
          borderRightColor={colorMode === "light" ? "gray.300" : "transparent"}
          borderRightWidth={1}
        >
          {/* left sidebar */}
          <NewChatButton />
          <NewAgentButton />
          <Divider
            borderColor={colorMode === "light" ? "gray.400" : "whiteAlpha.400"}
          />
          {leftPane}
          <Spacer />
          <Divider
            borderColor={colorMode === "light" ? "gray.400" : "whiteAlpha.400"}
          />
          <Navigation />
          <ColorModeButton />
        </VStack>
        <Flex
          direction="column"
          flex="1"
          h="100%"
          bg={colorMode === "light" ? "gray.100" : "gray.800"}
        >
          {/* main content area */}
          <Suspense fallback={<CenteredSpinner />}>{content}</Suspense>
        </Flex>
      </Flex>
    </SidebarProvider>
  );
};
