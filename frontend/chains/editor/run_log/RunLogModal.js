import React from "react";
import {
  Box,
  HStack,
  Text,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
} from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { RunLogStatusIcon, StatusIcon } from "chains/editor/run_log/icons";
import { RunLog } from "chains/editor/run_log/RunLog";
import { useRunLog } from "chains/editor/run_log/useRunLog";

export const RunLogModal = ({ children }) => {
  const { disclosure } = useRunLog();
  const { isOpen, onOpen, onClose } = disclosure;

  const { colorMode } = useColorMode();
  const highlightColor = colorMode === "light" ? "blue.500" : "blue.400";
  const color = colorMode === "light" ? "gray.800" : "white";

  return (
    <>
      <Box cursor={"pointer"} onClick={onOpen}>
        {children}
      </Box>
      <Modal isOpen={isOpen} onClose={onClose} size="6xl">
        <ModalOverlay />
        <ModalContent px={0}>
          <ModalHeader
            borderBottom="2px solid"
            borderColor={highlightColor}
            color={color}
          >
            <HStack>
              <RunLogStatusIcon /> <Text>Execution log</Text>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody px={0} pb={4}>
            <Box height={"calc(100vh - 250px)"} overflow={"hidden"}>
              {isOpen && <RunLog />}
            </Box>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
