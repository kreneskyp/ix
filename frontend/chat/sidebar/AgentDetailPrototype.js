import {Box, HStack, Text, useDisclosure} from "@chakra-ui/react";
import AgentDetailModalButton from "agents/AgentDetailModalButton";
import AssistantAvatar from "chat/AssistantAvatar";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faArrowsRotate, faCog, faStop, faTrash} from "@fortawesome/free-solid-svg-icons";
import React from "react";

const AgentListItem = ({ agent, onEdit, onDelete }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <AgentDetailModalButton agent={agent} width="100%">
      <Box
        bg="transparent"
        onMouseEnter={onOpen}
        onMouseLeave={onClose}
        _hover={{
          cursor: "pointer",
        }}
        width="100%"
        py={2}
      >
        <Box position="relative">
          <HStack>
            <AssistantAvatar agent={agent} /> <Text>{agent.name}</Text>
          </HStack>
          <Box
            position="absolute"
            right="0"
            top="-1"
            display={isOpen ? "flex" : "none"}
          >
            <Box p={1} ml={1} color="green.300">
              <FontAwesomeIcon
                icon={faStop}
                size="md"
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(agent);
                }}
              />
            </Box>
            <Box p={1} ml={1} color="green.300">
              <FontAwesomeIcon
                icon={faArrowsRotate}
                size="md"
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(agent);
                }}
              />
            </Box>
            <Box p={1} ml={1}>
              <FontAwesomeIcon
                icon={faCog}
                size="md"
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(agent);
                }}
              />
            </Box>
            <Box p={1} ml={1}>
              <FontAwesomeIcon
                icon={faTrash}
                size="md"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(agent);
                }}
              />
            </Box>
          </Box>
        </Box>
      </Box>
    </AgentDetailModalButton>