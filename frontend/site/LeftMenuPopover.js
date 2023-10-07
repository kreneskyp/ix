import React from "react";
import {
  useDisclosure,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverArrow,
  PopoverHeader as ChakraPopoverHeader,
  IconButton,
  useColorMode,
} from "@chakra-ui/react";

export const LeftSidebarPopupIcon = ({ children }) => {
  return children;
};

export const LeftSidebarPopupHeader = ({ children }) => {
  return children;
};

export const LeftSidebarPopupContent = ({ children }) => {
  return children;
};

export const LeftMenuPopover = ({ children }) => {
  const { isOpen, onToggle, onClose, onOpen } = useDisclosure();

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
  const style =
    colorMode === "light"
      ? { border: "1px solid", borderColor: "gray.300" }
      : { border: "1px solid", borderColor: "whiteAlpha.50" };
  const highlightColor = colorMode === "light" ? "blue.500" : "blue.400";
  const color = colorMode === "light" ? "gray.800" : "white";

  return (
    <Popover
      isOpen={isOpen}
      onClose={onClose}
      placement={"right-start"}
      closeOnBlur={false}
    >
      <PopoverTrigger>
        <IconButton icon={icon} {...style} onClick={onToggle} />
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
