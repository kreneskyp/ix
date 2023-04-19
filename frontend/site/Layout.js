import React, { Suspense } from "react";
import { Divider, Flex, Spacer, VStack } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import Navigation from "site/Navigation";
import { ColorModeButton } from "components/ColorModeButton";
import { CenteredSpinner } from "site/CenteredSpinner";

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
    <Flex h="100vh">
      <VStack
        bg={colorMode === "light" ? "blackAlpha.900" : "blackAlpha.600"}
        width={300}
        p={4}
        minH="100vh"
        align="left"
      >
        {/* left sidebar */}
        {leftPane}
        <Spacer />
        <Divider />
        <Navigation />
        <Divider />
        <ColorModeButton />
      </VStack>
      <Flex direction="column" flex="1" h="100%">
        {/* main content area */}
        <Suspense fallback={<CenteredSpinner />}>{content}</Suspense>
      </Flex>
    </Flex>
  );
};
