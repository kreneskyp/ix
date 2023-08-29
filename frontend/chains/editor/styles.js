import {
  faGear,
  faBrain,
  faChain,
  faDatabase,
  faFileImport,
  faFileWaveform,
  faMemory,
  faMessage,
  faRobot,
  faTools,
} from "@fortawesome/free-solid-svg-icons";
import { ChainNode } from "chains/flow/ChainNode";

export const NODE_STYLES = {
  llm: {
    icon: faBrain,
  },
  chain: {
    icon: faChain,
    component: ChainNode,
  },
  memory: {
    icon: faMemory,
  },
  memory_backend: {
    icon: faMemory,
  },
  prompt: {
    icon: faMessage,
    width: 400,
  },
  agent: {
    icon: faRobot,
    component: ChainNode,
  },
  parser: {
    icon: faFileWaveform,
  },
  document_loader: {
    icon: faFileImport,
  },
  retriever: {
    icon: faFileImport,
  },
  vectorstore: {
    icon: faDatabase,
  },
  text_splitter: {
    icon: faFileImport,
  },
  tool: {
    icon: faTools,
  },
  toolkit: {
    icon: faTools,
  },
  embeddings: {
    icon: faBrain,
  },
};

export const DEFAULT_NODE_STYLE = {
  icon: faGear,
};
