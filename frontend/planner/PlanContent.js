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
} from "@chakra-ui/react";
import { ChevronDownIcon, ChevronRightIcon } from "@chakra-ui/icons";
import AuthorizeCommandButton from "chat/AuthorizeCommandButton";

const StepDetails = ({ step }) => (
  <Card mt={5}>
    <CardHeader>
      <Text>
        <strong>Requires:</strong> {step.requires_artifacts?.join(", ")}
      </Text>
      <Text>
        <strong>Produces:</strong> {step.produces_artifacts?.join(", ")}
      </Text>
    </CardHeader>
    <CardBody>
      <Text mt={5}>
        <strong>Command:</strong> {step.command?.name}
      </Text>
      <Table variant="simple" size="sm">
        <Thead>
          <Tr>
            <Th>Argument</Th>
            <Th>Value</Th>
          </Tr>
        </Thead>
        <Tbody>
          {Object.entries(step.command?.args).map(([key, value]) => (
            <Tr key={key}>
              <Td>{key}</Td>
              <Td>{value}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </CardBody>
  </Card>
);

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
