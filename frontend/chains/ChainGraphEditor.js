import React, { useEffect, useState, useRef, useCallback } from "react";
import {v4 as uuid4} from 'uuid';
import { Box, Flex, Text } from "@chakra-ui/react";
import ReactFlow, {
  Background,
  Controls,
  ReactFlowProvider,
  useNodesState,
  useEdgesState,
} from "reactflow";
import ChainNode from "chains/flow/ChainNode";
import GroupNode from "chains/flow/GroupNode";
import LLMNode from "chains/flow/LLMNode";
import PromptNode from "chains/flow/PromptNode";

const nodeTypes = {
  chain: ChainNode,
  container: GroupNode,
  llm: LLMNode,
  prompt: PromptNode,
};

const ChainGraphEditor = () => {
  const initialNodes = [];

  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const config = JSON.parse(
        event.dataTransfer.getData("application/reactflow")
      );

      // check if the dropped element is valid
      if (typeof config.type === "undefined" || !config.type) {
        return;
      }

      console.log("DROPPED", config);

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });
      const newNode = {
        id: uuid4(),
        type: config.type,
        position,
        data: { config, node: config.default },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance]
  );

  return (
    <div className="dndflow">
      <ReactFlowProvider>
        <Box ref={reactFlowWrapper} width={1600} height={850}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
          >
            <Controls />
            <Background color="#aaa" gap={16} />
          </ReactFlow>
        </Box>
      </ReactFlowProvider>
    </div>
  );
};

export default ChainGraphEditor;
