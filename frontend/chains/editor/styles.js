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
  faArrowRightToBracket,
  faArrowRightFromBracket,
} from "@fortawesome/free-solid-svg-icons";
import { ChainNode } from "chains/flow/ChainNode";
import { BranchNode } from "chains/flow/BranchNode";
import { MapNode } from "chains/flow/MapNode";

export const NODE_STYLES = {
  llm: {
    icon: faBrain,
    component: ChainNode,
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
    component: ChainNode,
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
  document_transformer: {
    icon: faFileWaveform,
  },
  output_parser: {
    icon: faFileWaveform,
  },
  retriever: {
    icon: faFileImport,
    component: ChainNode,
  },
  vectorstore: {
    icon: faDatabase,
  },
  store: {
    icon: faDatabase,
  },
  text_splitter: {
    icon: faFileImport,
  },
  tool: {
    icon: faTools,
    component: ChainNode,
  },
  toolkit: {
    icon: faTools,
  },
  embeddings: {
    icon: faBrain,
  },
  branch: {
    icon: faArrowRightFromBracket,
    component: BranchNode,
  },
  map: {
    icon: faArrowRightToBracket,
    component: MapNode,
  },
};

export const DEFAULT_NODE_STYLE = {
  icon: faGear,
};
