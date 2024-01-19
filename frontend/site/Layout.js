import React, { Suspense } from "react";
import { Box, Divider, Flex, Spacer, VStack } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { ColorModeButton } from "components/ColorModeButton";
import { CenteredSpinner } from "site/CenteredSpinner";
import { NewChatButton } from "chat/buttons/NewChatButton";
import { NewAgentButton } from "agents/NewAgentButton";
import Navigation from "site/Navigation";
import SidebarProvider, { useLeftSidebarContext } from "site/sidebar/context";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowRight, faArrowLeft } from "@fortawesome/free-solid-svg-icons";
import { SchemasMenuItem } from "schemas/SchemaMenuItem";

export const LayoutLeftPane = ({ children }) => {
  return children;
};

export const LayoutContent = ({ children }) => {
  return children;
};

export const LeftSideBarToggle = () => {
  const leftSideBar = useLeftSidebarContext(); // "icons" or "text"

  const toggle = React.useCallback(() => {
    leftSideBar.setSize(leftSideBar.size === "icons" ? "text" : "icons");
  }, [leftSideBar.size]);

  return (
    <Box
      onClick={toggle}
      cursor={"pointer"}
      color={"gray.500"}
      width={leftSideBar.width}
      display={"flex"}
      justifyContent={"end"}
      transition="width 0.3s ease-out, max-width 0.3s ease-out"
    >
      <Box mr={2}>
        <FontAwesomeIcon
          icon={leftSideBar.size === "icons" ? faArrowRight : faArrowLeft}
          size={"xs"}
        />
      </Box>
    </Box>
  );
};

const LeftSidebar = ({ children }) => {
  const { colorMode } = useColorMode();
  const leftSideBar = useLeftSidebarContext(); // "icons" or "text"
  return (
    <VStack
      bg={colorMode === "light" ? "gray.200" : "blackAlpha.200"}
      p={1}
      minH="100vh"
      align="left"
      borderRightColor={colorMode === "light" ? "gray.300" : "transparent"}
      borderRightWidth={1}
      width={leftSideBar.width}
      maxWidth={leftSideBar.width}
      transition="width 0.3s ease-out, max-width 0.3s ease-out"
    >
      <LeftSideBarToggle />

      {/* left sidebar */}
      <NewChatButton />
      <NewAgentButton />
      <Divider
        borderColor={colorMode === "light" ? "gray.400" : "whiteAlpha.400"}
      />
      {children}
      <Divider />
      <SchemasMenuItem />
      <Spacer />
      <Divider
        borderColor={colorMode === "light" ? "gray.400" : "whiteAlpha.400"}
      />
      <Navigation />
      <ColorModeButton />
    </VStack>
  );
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
        <LeftSidebar>{leftPane}</LeftSidebar>
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
