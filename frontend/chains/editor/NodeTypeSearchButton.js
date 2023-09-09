import React, { useContext, useEffect } from "react";
import { NodeTypeSearch } from "chains/editor/NodeTypeSearch";
import {
  IconButton,
  Popover,
  PopoverArrow,
  PopoverCloseButton,
  PopoverContent,
  PopoverHeader,
  PopoverTrigger,
  useDisclosure,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSquarePlus } from "@fortawesome/free-solid-svg-icons";
import { useColorMode } from "@chakra-ui/color-mode";
import { SelectedNodeContext } from "chains/editor/contexts";

export const NodeTypeSearchButton = () => {
  const { isOpen, onToggle, onClose, onOpen } = useDisclosure();

  // auto-open when connector is [de]selected
  // HAX: couldn't get this to work when closeOnBlur={true}
  //      this behavior is mostly ok though so can revisit later
  //      to make popover pinning a toggle.
  const { selectedConnector } = useContext(SelectedNodeContext);
  useEffect(() => {
    if (selectedConnector && !isOpen) {
      onOpen();
    } else if (!selectedConnector) {
      onClose();
    }
  }, [selectedConnector]);

  const { colorMode } = useColorMode();
  const style =
    colorMode === "light"
      ? {
          border: "1px solid",
          borderColor: "gray.300",
        }
      : {
          border: "1px solid",
          borderColor: "whiteAlpha.50",
        };

  return (
    <Popover
      isOpen={isOpen}
      onClose={onClose}
      placement={"right-start"}
      closeOnBlur={true}
    >
      <PopoverTrigger>
        <IconButton
          icon={<FontAwesomeIcon size={"lg"} icon={faSquarePlus} />}
          {...style}
          onClick={onToggle}
          title={"Add components"}
        />
      </PopoverTrigger>
      <PopoverContent zIndex={99998} pb={2}>
        <PopoverHeader>Components</PopoverHeader>
        <PopoverArrow />
        <PopoverCloseButton />
        <NodeTypeSearch />
      </PopoverContent>
    </Popover>
  );
};
