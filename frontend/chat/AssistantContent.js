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
  const { onPaused } = useTextToSpeech();
  const { colorMode } = useColorMode();
  const { thoughts, command } = content;
  const args = command.args;

  const handleSpeak = () => {
    onPaused(() => {
      const speechText = thoughts.speak;
      if (speechText) {
        const utterance = new SpeechSynthesisUtterance(speechText);
        window.speechSynthesis.speak(utterance);
      }
    });
  };

  const labelColor = useColorModeValue("black", "blue.300");
  const textColor = useColorModeValue("gray.600", "gray.400");

  return (
    <VStack align="left" mt="4" pl={5}>
      <Text mb={5}>{thoughts.text}</Text>
      <Grid templateColumns="minmax(85px, max-content) 1fr" gap={1}>
        <GridItem>
          <Text color={labelColor}>
            <b>Reasoning:</b>
          </Text>
        </GridItem>
        <GridItem>
          <Text color={textColor}>{thoughts.reasoning}</Text>
        </GridItem>
        <GridItem>
          <Text color={labelColor}>
            <b>Criticism:</b>
          </Text>
        </GridItem>
        <GridItem>
          <Text color={textColor}>{thoughts.criticism}</Text>
        </GridItem>
        <GridItem>
          <Text color={labelColor}>
            <b>Command:</b>
          </Text>
        </GridItem>
        <GridItem>
          <Text color={textColor}>{command.name}</Text>
        </GridItem>
      </Grid>
      {command && (
        <Box padding={15}>
          <Table
            bg={colorMode === "light" ? "white" : "gray.900"}
            variant="simple"
            spacing="0"
            padding={15}
          >
            <Thead>
              <Tr>
                <Th px={2}>Argument</Th>
                <Th px={2}>Value</Th>
              </Tr>
            </Thead>
            <Tbody>
              {Object.entries(args || []).map(([name, value]) => (
                <Tr key={name}>
                  <Td px={2}>{name}</Td>
                  <Td px={2}>{value}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}
      {thoughts.speak && (
        <Flex justifyContent="flex-end" alignItems="center">
          <Button
            leftIcon={<Icon as={FontAwesomeIcon} icon={faVolumeUp} />}
            onClick={handleSpeak}
          >
            Speak
          </Button>
        </Flex>
      )}
    </VStack>
  );
};

export default AssistantContent;
