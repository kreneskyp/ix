import { OpenAIAgentConfigForm } from "agents/OpenAIAgentConfigForm";

export const LLM_NAME_MAP = {
  "langchain.chat_models.openai.ChatOpenAI": "Open AI",
};

export const AGENT_MODELS = {
  "gpt-3.5-turbo": {
    name: "GPT-3.5 Turbo",
    configComponent: OpenAIAgentConfigForm,
  },
  "gpt-4": {
    name: "GPT-4",
    configComponent: OpenAIAgentConfigForm,
  },
};
