import {
  faGear,
  faBrain,
  faChain,
  faDatabase,
  faFileImport,
  faFileWaveform,
  faKeyboard,
  faList,
  faTableList,
  faFile,
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
import { RootNode } from "chains/flow/RootNode";
import { LoopIcon } from "icons/LoopIcon";
import { SplitIcon } from "icons/SplitIcon";
import { MergeIcon } from "icons/MergeIcon";
import { GraphIcon } from "icons/GraphIcon";
import { GraphNode } from "chains/flow/GraphNode";

export const NODE_STYLES = {
  llm: {
    icon: faBrain,
    component: ChainNode,
  },
  chain: {
    icon: faChain,
    component: ChainNode,
  },
  data: {
    icon: faFile,
    component: ChainNode,
  },
  flow: {
    icon: {
      component: LoopIcon,
    },
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
    component: ChainNode,
  },
  document_transformer: {
    icon: faFileWaveform,
    component: ChainNode,
  },
  output_parser: {
    icon: faFileWaveform,
  },
  retriever: {
    icon: faFileImport,
    component: ChainNode,
  },
  schema: {
    icon: faFile,
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
    component: ChainNode,
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
    icon: {
      component: SplitIcon,
    },
    component: BranchNode,
  },
  graph: {
    icon: {
      component: GraphIcon,
    },
    component: GraphNode,
  },
  map: {
    icon: {
      component: MergeIcon,
    },
    component: MapNode,
  },
  root: {
    icon: faKeyboard,
    component: RootNode,
  },
};

export const DEFAULT_NODE_STYLE = {
  icon: faGear,
};
