import React, { useCallback, useContext } from "react";
import {
  Box,
  Button,
  HStack,
  Text,
  FormControl,
  FormLabel,
  VStack,
  Input,
  FormHelperText,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChain, faRobot } from "@fortawesome/free-solid-svg-icons";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { ChainState } from "chains/editor/contexts";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import { NameField } from "chains/editor/fields/NameField";
import { DescriptionField } from "chains/editor/fields/DescriptionField";
import { RequiredAsterisk } from "components/RequiredAsterisk";
import { useChainUpdate } from "chains/hooks/useChainUpdate";

const ChainExplanation = () => {
  return (
    <FormHelperText fontSize={"xs"}>
      Chains may be called via the API, or by other agents and chains with a{" "}
      <Text as={"span"} color={"blue.300"}>
        ChainReference
      </Text>{" "}
      component.
    </FormHelperText>
  );
};

const AgentExplanation = () => {
  return (
    <FormHelperText fontSize={"xs"}>
      Agents may be summoned to chat sessions for conversational interactions.
    </FormHelperText>
  );
};

const SaveModeChooser = ({ chain, onChange }) => {
  const { isLight, highlight } = useEditorColorMode();
  const bg = isLight
    ? { onColor: "#38A169", offColor: "gray.600" }
    : { onColor: "#38A169", offColor: "gray.600" };

  const isAgent = chain?.is_agent;
  const handleChange = useCallback(
    (value) => {
      onChange({
        ...chain,
        is_agent: value,
      });
    },
    [chain, onChange]
  );

  return (
    <FormControl>
      <FormLabel size="sm" justify="start">
        Chain Type <RequiredAsterisk />
      </FormLabel>
      <HStack justifyItems={"flex"}>
        <Box>
          <Button
            size="sm"
            onClick={() => {
              handleChange(true);
            }}
            color={isAgent ? "white" : "gray.400"}
            bg={isAgent ? highlight.agent : bg.offColor}
            _hover={{ bg: highlight.agent, color: "white" }}
          >
            <FontAwesomeIcon icon={faRobot} />
            <Text as={"span"} ml={1}>
              Agent
            </Text>
          </Button>
        </Box>
        <Box>
          <Button
            size="sm"
            onClick={() => {
              handleChange(false);
            }}
            color={isAgent === false ? "white" : "gray.400"}
            bg={isAgent === false ? highlight.chain : bg.offColor}
            _hover={{ bg: highlight.chain, color: "white" }}
          >
            <FontAwesomeIcon icon={faChain} />{" "}
            <Text as={"span"} ml={1}>
              Chain
            </Text>
          </Button>
        </Box>
      </HStack>
      <Box fontSize={"xs"} color={"gray.300"}>
        {isAgent ? <AgentExplanation /> : <ChainExplanation />}
      </Box>
    </FormControl>
  );
};

export const AliasField = ({ object, onChange }) => {
  const colorMode = useEditorColorMode();
  const handleChange = useCallback(
    (e) => {
      onChange({
        ...object,
        alias: e.target.value,
      });
    },
    [object, onChange]
  );

  let helperText = null;
  if (object?.alias) {
    helperText = (
      <FormHelperText fontSize={"xs"}>
        This agent responds to the alias{" "}
        <Text as={"span"} color={"blue.300"}>
          @{object?.alias}
        </Text>{" "}
        in chat
      </FormHelperText>
    );
  } else {
    helperText = (
      <FormHelperText fontSize={"xs"}>
        Set{" "}
        <Text as={"span"} color={"blue.400"}>
          @alias
        </Text>{" "}
        to reference the agent in chat sessions
      </FormHelperText>
    );
  }

  return (
    <FormControl id="alias">
      <FormLabel>
        Alias <RequiredAsterisk />
      </FormLabel>
      <Input
        placeholder="Enter agent alias"
        value={object?.alias || ""}
        onChange={handleChange}
        {...colorMode.input}
      />
      {helperText}
    </FormControl>
  );
};

export const ChainEditorPane = () => {
  const [chain, setChain] = useContext(ChainState);
  const api = useContext(ChainEditorAPIContext);
  const onChainUpdate = useChainUpdate(chain, setChain, api);
  const { scrollbar } = useEditorColorMode();

  return (
    <VStack spacing={5}>
      <SaveModeChooser chain={chain} onChange={onChainUpdate} />
      {chain?.is_agent && (
        <AliasField object={chain} onChange={onChainUpdate} />
      )}
      <NameField object={chain} onChange={onChainUpdate} />
      <DescriptionField
        object={chain}
        onChange={onChainUpdate}
        minH={500}
        css={scrollbar}
      />
    </VStack>
  );
};
