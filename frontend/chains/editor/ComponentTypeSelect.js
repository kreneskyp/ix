import React from "react";
import { Select, components } from "chakra-react-select";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleQuestion } from "@fortawesome/free-solid-svg-icons";
import { Box, HStack, Text, useTheme } from "@chakra-ui/react";

import { useEditorColorMode } from "chains/editor/useColorMode";
import { NODE_STYLES } from "chains/editor/styles";
import { MenuList } from "components/select/MenuList";
import { useSelectStyles } from "components/select/useSelectStyles";

const AGENT_HELP_TEXT =
  "Agents may be summoned to chat sessions for conversational interactions.";
const CHAIN_HELP_TEXT =
  "Chains may be called via the API, or by other agents and chains with a ChainReference component.";
const DOCUMENT_LOADER_HELP_TEXT =
  "Document loaders fetch documents from a filesystem or service";
const EMBEDDINGS_HELP_TEXT = "Embeddings convert text into vectors";
const LLM_HELP_TEXT =
  "LLM are generative AI models that accept a prompt and generate text or other outputs";
const MEMORY_HELP_TEXT =
  "Memory components store & retrieve chat messages for use in conversational interactions";
const MEMORY_BACKEND_HELP_TEXT =
  "Memory backends interface with external services to store messages for a memory component";
const OUTPUT_PARSER_HELP_TEXT =
  "Output parsers transform the output of a chain.";
const PARSER_HELP_TEXT = "Parsers transform text.";
const PROMPT_HELP_TEXT = "Prompt templates render input for LLM models";
const RETRIEVER_HELP_TEXT =
  "Retrievers fetch documents from a service or store such as a VectorStore or database";
const STORE_HELP_TEXT = "Backend service that stores documents or other data";
const TOOL_HELP_TEXT =
  "Tools are used to perform actions such as sending emails or making API calls";
const DOCUMENT_TRANSFORMER_HELP_TEXT = "Transformer that operates on documents";
const VECTORSTORE_HELP_TEXT = "VectorStores store and retrieve vectors";

export const COMPONENT_TYPE_OPTIONS = [
  { value: "agent", label: "Agent", helpText: AGENT_HELP_TEXT },
  { value: "chain", label: "Chain", helpText: CHAIN_HELP_TEXT },
  { value: "prompt", label: "Prompt", helpText: PROMPT_HELP_TEXT },
  { value: "tool", label: "Tool", helpText: TOOL_HELP_TEXT },
  { value: "llm", label: "LLM", helpText: LLM_HELP_TEXT },
  { value: "memory", label: "Memory", helpText: MEMORY_HELP_TEXT },
  {
    value: "memory_backend",
    label: "Memory Backend",
    helpText: MEMORY_BACKEND_HELP_TEXT,
  },
  {
    value: "document_loader",
    label: "Document Loader",
    helpText: DOCUMENT_LOADER_HELP_TEXT,
  },
  { value: "embeddings", label: "Embeddings", helpText: EMBEDDINGS_HELP_TEXT },
  {
    value: "output_parser",
    label: "Output Parser",
    helpText: OUTPUT_PARSER_HELP_TEXT,
  },
  { value: "parser", label: "Parser", helpText: PARSER_HELP_TEXT },
  { value: "retriever", label: "Retriever", helpText: RETRIEVER_HELP_TEXT },
  { value: "store", label: "Store", helpText: STORE_HELP_TEXT },
  {
    value: "document_transformer",
    label: "Document Transformer",
    helpText: DOCUMENT_TRANSFORMER_HELP_TEXT,
  },
  {
    value: "vectorstore",
    label: "Vectorstore",
    helpText: VECTORSTORE_HELP_TEXT,
  },
];

export const getOptionStyle = (isLight) => {
  return isLight
    ? {
        hover: {
          bg: "blackAlpha.100",
        },
        label: {
          color: "gray.600",
        },
        container: {
          color: "gray.700",
        },
        help: {
          color: "gray.500",
        },
        icon: {
          color: "gray.600",
        },
      }
    : {
        hover: {
          bg: "blackAlpha.300",
        },
        label: {
          color: "gray.300",
        },
        help: {
          color: "gray.500",
        },
        icon: {
          color: "gray.300",
        },
      };
};

export const findOption = (value) => {
  return COMPONENT_TYPE_OPTIONS.find((option) => option.value === value);
};

const ValueContainer = ({ children, ...props }) => {
  const { getValue } = props;
  const value = getValue()[0];
  const { isLight, highlight } = useEditorColorMode();
  const iconColor = isLight ? "gray.100" : "gray.100";

  return (
    <components.ValueContainer {...props}>
      <HStack p={0} m={0}>
        {value ? (
          <Box
            bg={highlight[value.value] || highlight.default}
            pl={2}
            m={0}
            height={"38px"}
            display="flex"
            alignItems="center"
            justifyContent="center"
            color={iconColor}
          >
            <FontAwesomeIcon
              icon={NODE_STYLES[value.value]?.icon || faCircleQuestion}
              style={{ marginRight: "8px" }}
            />
          </Box>
        ) : null}
        {children}
      </HStack>
    </components.ValueContainer>
  );
};

export const ComponentTypeSelect = ({ chain, onChange, value, ...props }) => {
  const { input: styles } = useEditorColorMode();
  const chakraStyles = {
    control: (base) => ({ ...base, ...styles, width: 400 }),
    dropdownIndicator: (base) => ({ ...base, ...styles }),
  };
  const selectStyles = useSelectStyles();

  const CustomOption = React.useMemo(() => {
    const onClick = (newValue) => {
      onChange({ type: newValue.value });
    };

    return ({ data }) => {
      const { isLight, highlight } = useEditorColorMode();
      const style = getOptionStyle(isLight);

      return (
        <HStack
          my={3}
          cursor={"pointer"}
          _hover={style.hover}
          onClick={() => onClick(data)}
          borderLeft={"6px solid"}
          borderLeftColor={highlight[data.value]}
        >
          <Box>
            <Text p={3} {...style.icon}>
              <FontAwesomeIcon
                icon={NODE_STYLES[data.value]?.icon || faCircleQuestion}
              />
            </Text>
          </Box>
          <Box>
            <Text fontWeight="bold" {...style.label}>
              {data.label}
            </Text>
            <Text fontSize="xs" {...style.help}>
              {data.helpText}
            </Text>
          </Box>
        </HStack>
      );
    };
  }, [chain, onChange]);

  return (
    <Box width={"100%"} {...props}>
      <Select
        default={"agent"}
        options={COMPONENT_TYPE_OPTIONS}
        value={findOption(chain?.type || "agent")}
        styles={selectStyles}
        menuPortalTarget={document.body}
        chakraStyles={chakraStyles}
        components={{ Option: CustomOption, MenuList, ValueContainer }}
      />
    </Box>
  );
};
