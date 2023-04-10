import React from "react";
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Box,
  Flex,
  Button,
  Icon,
  GridItem,
  Text,
  Grid,
  VStack,
} from "@chakra-ui/react";
import { faVolumeUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import useTextToSpeech from "chat/useTextToSpeech";

const AssistantContent = ({ content }) => {
  const { onPaused } = useTextToSpeech();

  const { thoughts, command } = content;
  const args = JSON.parse(command.args);

  const handleSpeak = () => {
    onPaused(() => {
      const speechText = thoughts.speak;
      if (speechText) {
        const utterance = new SpeechSynthesisUtterance(speechText);
        window.speechSynthesis.speak(utterance);
      }
    });
  };

  return (
    <VStack align="left" mt="4" pl={5}>
      <Text mb={5}>{thoughts.text}</Text>
      <Grid templateColumns="minmax(85px, max-content) 1fr" gap={1}>
        <GridItem>
          <Text>
            <b>Reasoning:</b>
          </Text>
        </GridItem>
        <GridItem>
          <Text>{thoughts.reasoning}</Text>
        </GridItem>
        <GridItem>
          <Text>
            <b>Criticism:</b>
          </Text>
        </GridItem>
        <GridItem>
          <Text>{thoughts.criticism}</Text>
        </GridItem>
        <GridItem>
          <Text>
            <b>Command:</b>
          </Text>
        </GridItem>
        <GridItem>
          <Text>{command.name}</Text>
        </GridItem>
      </Grid>
      {command && (
        <Table
          borderWidth="1px"
          borderColor="gray.200"
          borderRadius="md"
          bg="white"
          variant="simple"
          spacing="0"
        >
          <Thead>
            <Tr>
              <Th px={2}>Argument</Th>
              <Th px={2}>Value</Th>
            </Tr>
          </Thead>
          <Tbody>
            {Object.entries(args).map(([name, value]) => (
              <Tr key={name}>
                <Td px={2}>{name}</Td>
                <Td px={2}>{value}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
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
