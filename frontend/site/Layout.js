import React, { Suspense } from "react";
import { Button, Divider, Flex, Icon, Spacer, VStack } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import Navigation from "site/Navigation";
import { ColorModeButton } from "components/ColorModeButton";
import { CenteredSpinner } from "site/CenteredSpinner";
import { Link } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus, faVolumeUp } from "@fortawesome/free-solid-svg-icons";

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
        <Link to="/tasks/new">
          <Button
            bg="transparent"
            width="100%"
            borderStyle="dashed"
            borderWidth="2px"
            borderColor="whiteAlpha.600"
            color="whiteAlpha.800"
            leftIcon={<Icon as={FontAwesomeIcon} icon={faPlus} />}
          >
            New Task
          </Button>
        </Link>
        <Divider />
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
