import React, { useEffect, useState, useRef, useCallback } from "react";
import { v4 as uuid4 } from "uuid";
import { Box, Flex, Text, useToast } from "@chakra-ui/react";
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
import { useChainEditorAPI } from "chains/hooks/useChainEditorAPI";
import { useNavigate } from "react-router-dom";

const nodeTypes = {
  chain: ChainNode,
  container: GroupNode,
  llm: LLMNode,
  prompt: PromptNode,
};

const toData = (chain, node) => ({
  id: node.id,
  //nodeType: "node",
  chainId: chain?.id || null,
  classPath: node.data.config.default.classPath,
  position: node.position,
  config: node.data.config.default.config,
});

const ChainGraphEditor = ({ chain, initialNodes, initialEdges }) => {
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes || []);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges || []);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const toast = useToast();
  const navigate = useNavigate();

  const onAPIError = useCallback((err) => {
    toast({
      title: "Error",
      description: `Failed to save chain. ${err.message}`,
      status: "error",
      duration: 10000,
      isClosable: true,
    });
  });

  const api = useChainEditorAPI({ chain, onError: onAPIError });

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onNodeSaved = useCallback(
    ({ addChainNode }) => {
      // first node creates the new chain
      // redirect to the correct URL
      const { node } = addChainNode;
      const chain_id = node?.chain?.id;

      if (chain_id && chain === undefined) {
        navigate(`/proto/${chain_id}`, { replace: true });
      }
    },
    [chain?.id]
  );

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

      const data = {
        id: node.id,
        // nodeType: "node",
        chainId: chain?.id || null,
        classPath: node.data.config.default.classPath,
        position: node.position,
        config: node.data.config.default.config,
      };
      api.addNode(data, { onCompleted: onNodeSaved });
    },
    [reactFlowInstance]
  );

  const onNodeDragStop = useCallback((event, node) => {
    const data = {
      id: node.id,
      //nodeType: "node",
      classPath: node.classPath,
      description: node.description,
      position: node.position,
      config: node.config,
    };
    api.updateNode(data);
  }, []);

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
            onNodeDragStop={onNodeDragStop}
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
