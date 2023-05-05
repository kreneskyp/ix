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
  Card,
  CardHeader,
  CardBody,
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
  return (
    <Box mt={5}>
      <Grid templateColumns="max-content 1fr" gap={3}>
        <Text fontWeight="bold" justifySelf="left">
          Requires:
        </Text>
        <Text gridColumn="2 / 3">{step.requires_artifacts?.join(", ")}</Text>
        <Text fontWeight="bold" justifySelf="left">
          Produces:
        </Text>
        <Text gridColumn="2 / 3">{step.produces_artifacts?.join(", ")}</Text>
        <Text fontWeight="bold" justifySelf="left">
          Command:
        </Text>
        <Text gridColumn="2 / 3">{step.command?.name}</Text>
      </Grid>
      <Table variant="simple" size="sm" borderWidth="0px" my={5}>
        <Thead>
          <Tr>
            <Th borderBottomWidth="1px">Argument</Th>
            <Th borderBottomWidth="1px">Value</Th>
          </Tr>
        </Thead>
        <Tbody>
          {Object.entries(step.command?.args).map(([key, value]) => (
            <Tr key={key}>
              <Td border={0}>{key}</Td>
              <Td border={0}>
                <SyntaxHighlighter style={syntaxTheme} wrapLines={true}>
                  {value}
                </SyntaxHighlighter>
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

  const handleExpand = (index) => {
    if (expandedStep === index) {
      setExpandedStep(null);
    } else {
      setExpandedStep(index);
    }
  };

  return (
    <Box>
      Here is a plan for your request:
      <Table variant="simple" borderBottom={0}>
        <Thead>
          <Tr>
            <Th>#</Th>
            <Th>Description</Th>
          </Tr>
        </Thead>
        <Tbody>
          {message.content.steps.map((step, index) => (
            <React.Fragment key={index}>
              <Tr
                onClick={() => handleExpand(index)}
                borderTop={expandedStep === index ? "none" : "1px solid"}
                borderColor="gray.200"
              >
                <Td>{index + 1}</Td>
                <Td>
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
                  <Collapse in={expandedStep === index} paddingTop="1px">
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
