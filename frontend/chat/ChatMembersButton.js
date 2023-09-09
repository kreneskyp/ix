import React from "react";
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
import { faSquarePlus, faUsers } from "@fortawesome/free-solid-svg-icons";
import { useColorMode } from "@chakra-ui/color-mode";
import { NodeTypeSearch } from "chains/editor/NodeTypeSearch";
import SideBarAgentList from "chat/sidebar/SideBarAgentList";

export const ChatMembersButton = ({ graph, loadGraph }) => {
  const { isOpen, onToggle, onClose } = useDisclosure();

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
      closeOnBlur={false}
    >
      <PopoverTrigger>
        <IconButton
          icon={<FontAwesomeIcon size={"lg"} icon={faUsers} />}
          {...style}
          onClick={onToggle}
          title={"Chat members"}
        />
      </PopoverTrigger>
      <PopoverContent zIndex={99998} pb={2}>
        <PopoverHeader>Assistants</PopoverHeader>
        <PopoverArrow />
        <PopoverCloseButton />
        <SideBarAgentList graph={graph} loadGraph={loadGraph} />
      </PopoverContent>
    </Popover>
  );
};
