import React, { useEffect, useState, useRef, useCallback } from "react";

import { HStack, Text, VStack } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBrain,
  faChain,
  faMemory,
  faMessage,
  faPlus,
  faRobot,
  faToolbox,
  faTools,
} from "@fortawesome/free-solid-svg-icons";
import { NodeSelector } from "chains/editor/NodeSelector";
import {
  useEditorColorMode,
  useSideBarColorMode,
} from "chains/editor/useColorMode";

const LLMNodeTypes = [
  {
    label: "OpenAI",
    type: "llm",
    options: {
      models: [
        { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
        { value: "gpt-4", label: "GPT-4" },
      ],
    },
    default: {
      classPath: "langchain.chat_models.openai.ChatOpenAI",
      model: "gpt-4",
      config: {
        temperature: 0,
        max_tokens: 100,
        top_p: 1,
        frequency_penalty: 0,
        presence_penalty: 0,
        stop_words: "",
        request_timeout: 60,
        verbose: false,
      },
    },
  },
  { label: "PaLM-2", type: "llm" },
];

const ChainNodeTypes = [
  {
    label: "LLMReply",
    type: "chain",
    default: {
      name: "",
      classPath: "ix.chains.llm.LLMReply",
      config: { llm: null },
    },
  },
  {
    label: "LLMToolChain",
    type: "chain",
    default: {
      name: "",
      classPath: "ix.chains.llm.LLMToolChain",
      config: { llm: null },
    },
  },
  {
    label: "LLMChain",
    type: "chain",
    default: {
      name: "",
      classPath: "ix.chains.tool_chain.LLMChain",
      config: { llm: null },
    },
  },
];

const PromptNodeTypes = [
  {
    label: "ChatPrompt",
    type: "prompt",
    default: {
      messages: null,
    },
  },
];

const AgentNodeTypes = [];

export const NodeSelectorHeader = ({ label, icon, highlight }) => {
  const { bg, color } = useSideBarColorMode();

  return (
    <HStack
      sx={{ userSelect: "none" }}
      width="100%"
      color={color}
      borderBottom="1px solid"
      borderColor="gray.600"
      px={2}
      pt={1}
    >
      <FontAwesomeIcon icon={icon} />
      <Text>{label}</Text>
    </HStack>
  );
};

export const NodeSelectorList = ({ nodeTypes }) => {
  return (
    <VStack spacing={0}>
      {nodeTypes.map((config, i) => {
        return <NodeSelector key={config.label} config={config} />;
      })}
    </VStack>
  );
};

export const ChainGraphEditorSideBar = () => {
  const { highlight } = useEditorColorMode();

  return (
    <VStack justifyItems="left">
      <NodeSelectorHeader
        label="Chain"
        icon={faChain}
        highlight={highlight.chain}
      />
      <NodeSelectorList nodeTypes={ChainNodeTypes} />
      <NodeSelectorHeader
        label="LLM"
        icon={faBrain}
        highlight={highlight.llm}
      />
      <NodeSelectorList nodeTypes={LLMNodeTypes} />
      <NodeSelectorHeader
        label="Prompts"
        icon={faMessage}
        highlight={highlight.prompt}
      />
      <NodeSelectorList nodeTypes={PromptNodeTypes} />
      <NodeSelectorHeader
        label="Agent"
        icon={faRobot}
        highlight={highlight.agent}
      />
      <NodeSelectorHeader
        label="Memory"
        icon={faMemory}
        highlight={highlight.memory}
      />
      <NodeSelectorHeader
        label="Tool"
        icon={faTools}
        highlight={highlight.tool}
      />
    </VStack>
  );
};
