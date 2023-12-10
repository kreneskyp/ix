import React from "react";
import {
  useDisclosure,
  Box,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverArrow,
  PopoverHeader as ChakraPopoverHeader,
  useColorMode,
} from "@chakra-ui/react";
import { useLeftSidebarContext } from "site/sidebar/context";

export const LeftSidebarPopupIcon = ({ children }) => {
  return children;
};

export const LeftSidebarPopupHeader = ({ children }) => {
  return children;
};

export const LeftSidebarPopupContent = ({ children }) => {
  return children;
};

export const LeftMenuPopover = ({ children, onOpen }) => {
  const { isOpen, onToggle, onClose } = useDisclosure();
  const sideBar = useLeftSidebarContext();

  const icon = React.Children.toArray(children).find(
    (child) => child.type === LeftSidebarPopupIcon
  );
  const content = React.Children.toArray(children).find(
    (child) => child.type === LeftSidebarPopupContent
  );
  const popoverHeader = React.Children.toArray(children).find(
    (child) => child.type === LeftSidebarPopupHeader
  );

  const { colorMode } = useColorMode();
  const highlightColor = colorMode === "light" ? "blue.500" : "blue.400";
  const color = colorMode === "light" ? "gray.800" : "white";
  const width = sideBar.size === "icons" ? "25px" : "110px";

  return (
    <Popover
      isOpen={isOpen}
      onClose={onClose}
      placement={"right-start"}
      closeOnBlur={false}
      onOpen={onOpen}
    >
      <PopoverTrigger>
        <Box
          onClick={onToggle}
          width={width}
          transition="width 0.3s ease-out, max-width 0.3s ease-out"
        >
          {icon}
        </Box>
      </PopoverTrigger>
      <PopoverContent
        zIndex={99998}
        pb={2}
        boxShadow="0px 0px 10px 0px rgba(0,0,0,0.15)"
        width={"100%"}
      >
        <ChakraPopoverHeader
          borderBottom="2px solid"
          borderColor={highlightColor}
          color={color}
        >
          {popoverHeader}
        </ChakraPopoverHeader>
        <PopoverArrow />
        {content}
      </PopoverContent>
    </Popover>
  );
};
