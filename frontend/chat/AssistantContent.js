import React from "react";
import { Button, Flex, Heading, Icon, Text } from "@chakra-ui/react";
import { faVolumeUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import useTextToSpeech from "chat/useTextToSpeech";

const AssistantContent = ({ thoughts, command }) => {
  const { onPaused } = useTextToSpeech();

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
    <Flex align="center" mt="4">
      <Flex
        w="14"
        h="14"
        borderRadius="full"
        bg="gray.200"
        justify="center"
        align="center"
        mr="4"
      >
        <Text fontSize="xl" fontWeight="bold" color="gray.500">
          {thoughts.text}
        </Text>
      </Flex>
      <Flex direction="column">
        <Heading as="h3" fontSize="lg" mb="2">
          {command ? command.name : thoughts.text}
        </Heading>
        {command && (
          <Flex direction="column">
            <Text mb="2" fontWeight="bold">
              Arguments:
            </Text>
            <Flex direction="column" mb="4">
              {Object.entries(command.args).map(([name, value]) => (
                <Text key={name}>
                  {name}: {value}
                </Text>
              ))}
            </Flex>
          </Flex>
        )}
        <Text mb="2">{thoughts.reasoning}</Text>
        <Text mb="2">
          Plan:
          <ul>
            {thoughts.plan.split("\n").map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </Text>
        <Text mb="2">{thoughts.criticism}</Text>
        {thoughts.speak && (
          <Button
            leftIcon={<Icon as={FontAwesomeIcon} icon={faVolumeUp} />}
            onClick={handleSpeak}
          >
            Speak
          </Button>
        )}
      </Flex>
    </Flex>
  );
};

export default AssistantContent;
