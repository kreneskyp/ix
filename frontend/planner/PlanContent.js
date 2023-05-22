import React, { useState } from "react";
import {
  Box,
  Table,
  Text,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Collapse,
  IconButton,
  Flex,
  Grid,
} from "@chakra-ui/react";
import { ChevronDownIcon, ChevronRightIcon } from "@chakra-ui/icons";
import AuthorizeCommandButton from "chat/AuthorizeCommandButton";

import SyntaxHighlighter from "react-syntax-highlighter";
import {
  stackoverflowLight,
  stackoverflowDark,
} from "react-syntax-highlighter/dist/esm/styles/hljs";
import { useColorMode } from "@chakra-ui/color-mode";

const StepDetails = ({ step }) => {
  const { colorMode } = useColorMode();
  const syntaxTheme =
    colorMode === "light" ? stackoverflowLight : stackoverflowDark;

  const artifactColor = colorMode === "light" ? "blue.500" : "blue.300";

  return (
    <Box mt={5}>
      <Grid templateColumns="max-content 1fr" gap={3}>
        <Text fontWeight="bold" justifySelf="left">
          Requires:
        </Text>
        <Text gridColumn="2 / 3">
          {step.requires_artifacts?.map((artifact, i) => (
            <Text key={i} as="span" color={artifactColor} mr={3}>
              {artifact}
            </Text>
          ))}
        </Text>
        <Text fontWeight="bold" justifySelf="left">
          Produces:
        </Text>
        <Text gridColumn="2 / 3">
          {step.produces_artifacts?.map((artifact, i) => (
            <Text key={i} as="span" color={artifactColor} mr={3}>
              {artifact.identifier}{" "}
            </Text>
          ))}
        </Text>
        <Text fontWeight="bold" justifySelf="left">
          Command:
        </Text>
        <Text gridColumn="2 / 3">{step.command?.name}</Text>
      </Grid>
      <Table variant="simple" size="sm" borderWidth="0px" my={5}>
        <Thead>
          <Tr>
            <Th
              borderBottomWidth="1px"
              borderColor={colorMode === "light" ? "gray.300" : "gray.600"}
            >
              Argument
            </Th>
            <Th
              borderBottomWidth="1px"
              borderColor={colorMode === "light" ? "gray.300" : "gray.600"}
            >
              Value
            </Th>
          </Tr>
        </Thead>
        <Tbody>
          {Object.entries(step.command?.args).map(([key, value]) => (
            <Tr key={key}>
              <Td border={0}>{key}</Td>
              <Td border={0}>
                <Box
                  sx={{ overflowX: "auto" }}
                  width={500}
                  border="1px solid"
                  borderColor={colorMode === "light" ? "gray.300" : "black"}
                >
                  <SyntaxHighlighter style={syntaxTheme} wrapLines={true}>
                    {value}
                  </SyntaxHighlighter>
                </Box>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

export const PlanContent = ({ message }) => {
  const [expandedStep, setExpandedStep] = useState(null);
  const { colorMode } = useColorMode();

  const handleExpand = (index) => {
    if (expandedStep === index) {
      setExpandedStep(null);
    } else {
      setExpandedStep(index);
    }
  };

  const borderColor = colorMode === "light" ? "gray.300" : "gray.600";

  return (
    <Box>
      Here is a plan for your request:
      <Table variant="simple" borderBottom={0}>
        <Thead>
          <Tr>
            <Th borderColor={borderColor}>#</Th>
            <Th borderColor={borderColor}>Description</Th>
          </Tr>
        </Thead>
        <Tbody>
          {message.content.steps.map((step, index) => (
            <React.Fragment key={index}>
              <Tr onClick={() => handleExpand(index)}>
                <Td width={50} borderColor={borderColor}>
                  {index + 1}
                </Td>
                <Td borderColor={borderColor}>
                  <Box>
                    {step.name}
                    <IconButton
                      icon={
                        expandedStep === index ? (
                          <ChevronDownIcon />
                        ) : (
                          <ChevronRightIcon />
                        )
                      }
                      size="sm"
                      variant="ghost"
                      float="right"
                    />
                  </Box>
                  <Collapse in={expandedStep === index}>
                    <StepDetails step={step} />
                  </Collapse>
                </Td>
              </Tr>
            </React.Fragment>
          ))}
        </Tbody>
      </Table>
      <Flex m={5} mb={2} justifyContent="flex-end">
        <AuthorizeCommandButton messageId={message.id} />
      </Flex>
    </Box>
  );
};
