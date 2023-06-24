import {
  faGear,
  faBrain,
  faChain,
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
  },
  tool: {
    icon: faTools,
  },
};

export const DEFAULT_NODE_STYLE = {
  icon: faGear,
};
