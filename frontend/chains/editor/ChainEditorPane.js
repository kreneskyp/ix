import React, { useCallback, useContext } from "react";
import {
  Box,
  Button,
  HStack,
  useDisclosure,
  Text,
  FormControl,
  FormLabel,
  Textarea,
  VStack,
  Input,
  FormHelperText,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChain, faRobot } from "@fortawesome/free-solid-svg-icons";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { ChainState } from "chains/editor/contexts";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import { useDebounce } from "utils/hooks/useDebounce";
import { CollapsibleSection } from "chains/flow/CollapsibleSection";
import { NameField } from "chains/editor/fields/NameField";
import { DescriptionField } from "chains/editor/fields/DescriptionField";
import { RequiredAsterisk } from "components/RequiredAsterisk";
import { useChainUpdate } from "chains/hooks/useChainUpdate";
import { getLabel } from "json_form/utils";
import { ComponentTypeSelect } from "chains/editor/ComponentTypeSelect";

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

export const ComponentTypeField = ({ chain, onChange }) => {
  const handleChange = useCallback(
    (values) => {
      onChange({
        ...chain,
        ...values,
      });
    },
    [chain]
  );

  return (
    <FormControl id="type">
      <FormLabel>
        Type <RequiredAsterisk />
      </FormLabel>
      <ComponentTypeSelect chain={chain} onChange={handleChange} />
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
  const { chain, setChain } = useContext(ChainState);
  const api = useContext(ChainEditorAPIContext);
  const onChainUpdate = useChainUpdate(chain, setChain, api);
  const { scrollbar } = useEditorColorMode();
  return (
    <VStack spacing={5}>
      <ComponentTypeField chain={chain} onChange={onChainUpdate} />
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
