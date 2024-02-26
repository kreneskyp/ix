import React from "react";
import { HStack, VStack, Text } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faKeyboard } from "@fortawesome/free-solid-svg-icons";
import { OutputsConnectors } from "chains/flow/FlowNode";

const ConnectorLabel = ({ value }) => {
  const label = typeof value === "object" ? value?.value : value;
  const isChat = value?.is_chat === true;
  return (
    <HStack>
      {isChat && (
        <Text>
          <FontAwesomeIcon icon={faKeyboard} />
        </Text>
      )}
      <Text>{label}</Text>
    </HStack>
  );
};

export const RootNode = ({ node }) => {
  return (
    <VStack spacing={0} alignItems="stretch" fontSize="xs">
      <OutputsConnectors node={node} connector_label={ConnectorLabel} />
    </VStack>
  );
};
