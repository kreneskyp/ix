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
import { faUsers } from "@fortawesome/free-solid-svg-icons";
import { useColorMode } from "@chakra-ui/color-mode";
import SideBarAgentList from "chat/sidebar/SideBarAgentList";

export const ChatMembersButton = ({ graph, onUpdateAgents, agentPage }) => {
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
        <IconButton
          icon={<FontAwesomeIcon size={"lg"} icon={faUsers} />}
          {...style}
          onClick={onToggle}
          title={"Chat members"}
        />
      </PopoverTrigger>
      <PopoverContent
        zIndex={99998}
        pb={2}
        boxShadow="0px 0px 10px 0px rgba(0,0,0,0.15)"
      >
        <PopoverHeader
          borderBottom="2px solid"
          borderColor={highlightColor}
          color={color}
        >
          Assistants
        </PopoverHeader>
        <PopoverArrow />
        <PopoverCloseButton />
        <SideBarAgentList
          graph={graph}
          onUpdateAgents={onUpdateAgents}
          agentPage={agentPage}
        />
      </PopoverContent>
    </Popover>
  );
};
