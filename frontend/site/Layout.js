import React, { Suspense } from "react";
import { Divider, Flex, Spacer, VStack } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import Navigation from "site/Navigation";
import { ColorModeButton } from "components/ColorModeButton";
import { CenteredSpinner } from "site/CenteredSpinner";
import { NewChatButton } from "chat/NewChatButton";

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
    <Flex h="100vh" overflowX="hidden">
      <VStack
        bg={colorMode === "light" ? "gray.300" : "gray.900"}
        width={300}
        p={2}
        minH="100vh"
        align="left"
      >
        {/* left sidebar */}
        <NewChatButton />
        {leftPane}
        <Spacer />
        <Divider
          borderColor={colorMode === "light" ? "gray.700" : "whiteAlpha.400"}
        />
        <Navigation />
        <Divider
          borderColor={colorMode === "light" ? "gray.700" : "whiteAlpha.400"}
        />
        <ColorModeButton />
      </VStack>
      <Flex
        direction="column"
        flex="1"
        h="100%"
        bg={colorMode === "light" ? "gray.200" : "gray.800"}
      >
        {/* main content area */}
        <Suspense fallback={<CenteredSpinner />}>{content}</Suspense>
      </Flex>
    </Flex>
  );
};
