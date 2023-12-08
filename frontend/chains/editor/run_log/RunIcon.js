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
  Tooltip,
  useDisclosure,
} from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import { ExecutionDetail } from "chains/editor/run_log/ExecutionDetail";
import { StatusIcon } from "chains/editor/run_log/icons";

export const RunIcon = ({ execution }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const { colorMode } = useColorMode();
  const highlightColor = colorMode === "light" ? "blue.500" : "blue.400";
  const color = colorMode === "light" ? "gray.800" : "white";

  return (
    <>
      <Tooltip label={"Success: run log"}>
        <Box cursor={"pointer"} onClick={onOpen}>
          <StatusIcon execution={execution} />
        </Box>
      </Tooltip>

      <Modal isOpen={isOpen} onClose={onClose} size="2xl">
        <ModalOverlay />
        <ModalContent px={0}>
          <ModalHeader
            borderBottom="2px solid"
            borderColor={highlightColor}
            color={color}
          >
            <HStack>
              <StatusIcon execution={execution} /> <Text>Execution log</Text>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody px={0} pb={4}>
            <ExecutionDetail execution={execution} />
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
