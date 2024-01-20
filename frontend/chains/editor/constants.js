import { OpenAIConfigForm } from "chains/editor/OpenAIConfigForm";

export const LLM_FORM_MAP = {
  "langchain.chat_models.openai.ChatOpenAI": OpenAIConfigForm,
};

export const NOTIFY_SAVED = {
  title: "Saved",
  description: "Saved",
  status: "success",
  duration: 2000,
  isClosable: true,
  position: "bottom-right",
};
