import React from "react";
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Flex,
  Button,
  Icon,
  GridItem,
  Text,
  Grid,
  VStack,
  Box,
  useColorModeValue,
} from "@chakra-ui/react";
import { faVolumeUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import useTextToSpeech from "chat/useTextToSpeech";
import { useColorMode } from "@chakra-ui/color-mode";

const AssistantContent = ({ content }) => {
  return <Text>{content.text}</Text>;
};

export default AssistantContent;
