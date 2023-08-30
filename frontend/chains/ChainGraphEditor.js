import React, { useState, useRef, useCallback, useContext } from "react";
import { v4 as uuid4 } from "uuid";
import { Box, Input } from "@chakra-ui/react";
import ReactFlow, {
  addEdge,
  updateEdge,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
} from "reactflow";
import ConfigNode from "chains/flow/ConfigNode";
import { useNavigate } from "react-router-dom";

import "reactflow/dist/style.css";
import "./styles.css";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import {
  getEdgeStyle,
  toReactFlowNode,
  useGraphForReactFlow,
} from "chains/hooks/useGraphForReactFlow";
import { useColorMode } from "@chakra-ui/color-mode";
import { RootNode } from "chains/flow/RootNode";
import { getDefaults } from "chains/flow/TypeAutoFields";
import { useDebounce } from "utils/hooks/useDebounce";
import { useAxios } from "utils/hooks/useAxios";
import { SelectedNodeContext } from "chains/editor/SelectedNodeContext";

// Nodes are either a single node or a group of nodes
// ConfigNode renders class_path specific content
const nodeTypes = {
  node: ConfigNode,
  list: ConfigNode,
  root: RootNode,
};

const getExpectedTypes = (connector) => {
  return Array.isArray(connector?.source_type)
    ? new Set(connector.source_type)
    : new Set([connector.source_type]);
};

const ChainGraphEditor = ({ graph, chain, setChain }) => {
  const reactFlowWrapper = useRef(null);
  const edgeUpdate = useRef(true);
  const [chainLoaded, setChainLoaded] = useState(graph?.chain !== undefined);
  const { call: loadChain } = useAxios();

  const reactFlowGraph = useGraphForReactFlow(graph);
  const [nodes, setNodes, onNodesChange] = useNodesState(reactFlowGraph.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(reactFlowGraph.edges);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const { colorMode } = useColorMode();
  const navigate = useNavigate();
  const api = useContext(ChainEditorAPIContext);
  const { selectedNode, selectedConnector, setSelectedConnector } =
    useContext(SelectedNodeContext);

  // handle dragging a node onto the graph
  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onNodeSaved = useCallback(
    (response) => {
      // first node creates the new chain
      // redirect to the correct URL
      if (!chainLoaded) {
        navigate(`/chains/${response.data.chain_id}`, { replace: true });
        loadChain(`/api/chains/${response.data.chain_id}`, {
          onSuccess: (response) => {
            setChain(response.data);
            setChainLoaded(true);
          },
        });
      }
    },
    [chain?.id, chainLoaded]
  );

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const nodeType = JSON.parse(
        event.dataTransfer.getData("application/reactflow")
      );

      // check if the dropped element is valid
      if (typeof nodeType.type === "undefined" || !nodeType.type) {
        return;
      }

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNodeID = uuid4();

      // auto edge connection. Prefer selected connector, then selected node
      let edge = null;
      let edgeConnector = null;
      if (selectedNode || selectedConnector) {
        const node = selectedConnector?.node || selectedNode?.data.node;
        if (selectedConnector) {
          edgeConnector = selectedConnector.connector;
        } else {
          // Only Node selected:
          // select the first open connector accepting the node type
          const targetType = selectedNode.data.type;
          edgeConnector = targetType.connectors.find((connector) =>
            getExpectedTypes(connector).has(nodeType.type)
          );
        }

        if (edgeConnector) {
          // output connector is a source, flip the edge
          const isOutput = edgeConnector.key === "out";
          const key = isOutput ? "in" : edgeConnector.key;
          const source_id = isOutput ? node.id : newNodeID;
          const target_id = isOutput ? newNodeID : node.id;
          const edgeId = uuid4();

          // TODO: implement edge validation
          const IS_VALID = true;
          if (IS_VALID) {
            edge = {
              id: edgeId,
              source_id,
              target_id,
              key,
            };
          }
        }
      }

      // create data object instead of waiting for graphql
      const data = {
        id: newNodeID,
        chain_id: chain?.id || null,
        class_path: nodeType.class_path,
        position: position,
        config: getDefaults(nodeType),
      };
      if (edge) {
        data.edges = [edge];
      }

      // create ReactFlow node
      const flowNode = toReactFlowNode(data, nodeType);

      // add to API and ReactFlow
      api.addNode(data, { onSuccess: onNodeSaved });
      setNodes((nds) => nds.concat(flowNode));

      if (edge) {
        const flowNodeType = nodeType.type;
        const style = getEdgeStyle(colorMode, flowNodeType);
        const flowEdge = {
          id: edge.id,
          type: "default",
          source: edge.source_id,
          target: edge.target_id,
          sourceHandle: edge.key === "in" ? "out" : flowNodeType,
          targetHandle: edge.key,
          data: { id: edge?.id },
          style,
        };
        setEdges((els) => addEdge(flowEdge, els));
      }
    },
    [reactFlowInstance, chain?.id, selectedNode, colorMode, selectedConnector]
  );

  const onFilteredNodesChange = useCallback(
    (flowNodes) => {
      // root node can't be moved.
      if (flowNodes[0].id === "root") {
        return;
      }
      return onNodesChange(flowNodes);
    },
    [onNodesChange]
  );

  const onNodeDragStop = useCallback((event, node) => {
    // update node with new position
    api.updateNodePosition(node.id, node.position);
  }, []);

  // new edges
  const onConnect = useCallback(
    (params) => {
      // create reactflow edge
      const id = uuid4();
      const source = reactFlowInstance.getNode(params.source);
      const flowNodeType =
        source.id === "root" ? "root" : source.data.type.type;
      const style = getEdgeStyle(colorMode, flowNodeType);
      setEdges((els) => addEdge({ ...params, data: { id }, style }, els));

      // save via API
      if (source.id === "root") {
        // link from root node uses setRoot since it's not stored as an edge
        api.setRoot(chain.id, { node_id: params.target });
      } else {
        // normal link and prop edges
        const data = {
          id,
          source_id: params.source,
          target_id: params.target,
          key: params.targetHandle,
          chain_id: chain?.id,
          relation: params.sourceHandle === "out" ? "LINK" : "PROP",
        };
        api.addEdge(data);
      }
    },
    [chain, reactFlowInstance, colorMode]
  );

  const isValidConnection = useCallback(
    // Connections are allowed when the source and target types match
    // and the target has an open connector slot. Targets may optionally
    // support multiple connections.

    (connection) => {
      // target
      const target = reactFlowInstance.getNode(connection.target);
      const connectors = target.data.type.connectors;
      let connector, expectedTypes;
      if (connection.targetHandle === "in") {
        expectedTypes = new Set(["chain-link"]);
      } else {
        connector = connectors.find((c) => c.key === connection.targetHandle);
        expectedTypes = Array.isArray(connector?.source_type)
          ? new Set(connector.source_type)
          : new Set([connector.source_type]);
      }
      const supportsMultiple = connector?.multiple || false;

      // source
      const source = reactFlowInstance.getNode(connection.source);
      const providedType =
        connection.sourceHandle === "out"
          ? "chain-link"
          : source.data.type.type;

      // connection types must match
      // HAX: adding a special case for chain-agent connections until expectedType can be
      //      expanded to be a set of types
      if (
        expectedTypes.has(providedType) ||
        (expectedTypes.has("chain") && providedType === "agent")
      ) {
        const instanceEdges = reactFlowInstance.getEdges();
        const targetEdges = instanceEdges.filter(
          (e) =>
            e.target === target.id && e.targetHandle === connection.targetHandle
        );
        const sourceEdges = instanceEdges.filter(
          (e) =>
            e.source === source.id && e.sourceHandle === connection.sourceHandle
        );
        const sourceConnected = sourceEdges.length > 0;
        const targetConnected = targetEdges.length > 0;

        if (edgeUpdate.edge) {
          // valid when updating an edge:
          // - if connecting to the same target/source
          // - if connecting to an unconnected target/source
          // - if target supports multiple connections
          const currentSource = edgeUpdate.edge.source;
          const currentTarget = edgeUpdate.edge.target;
          const isSameSource = connection.source === currentSource;
          const isSameTarget = connection.target === currentTarget;

          return (
            (isSameSource || !sourceConnected) &&
            (isSameTarget || !targetConnected || supportsMultiple)
          );
        } else {
          // valid when creating a new edge
          // - if connecting to an unconnected target/source
          // - if target supports multiple connections
          return !sourceConnected && (!targetConnected || supportsMultiple);
        }
      }

      return false;
    },
    [reactFlowInstance]
  );

  const onEdgeUpdateStart = useCallback(
    (event, edge) => {
      // reset flag when edge is grabbed
      edgeUpdate.edge = edge;
      edgeUpdate.toHandle = false;
    },
    [setEdges]
  );

  const onEdgeUpdate = useCallback(
    (oldEdge, newConnection) => {
      // update edge if dropped on valid handle
      edgeUpdate.toHandle = true;
      setEdges((els) => updateEdge(oldEdge, newConnection, els));
      if (newConnection.source === "root") {
        if (oldEdge.target !== newConnection.target) {
          api.setRoot({ chain_id: chain.id, node_id: newConnection.target });
        }
      } else {
        const isSame =
          oldEdge.source === newConnection.source &&
          oldEdge.target === newConnection.target;
        if (!isSame) {
          api.updateEdge(oldEdge.data.id, {
            source_id: newConnection.source,
            target_id: newConnection.target,
          });
        }
      }
    },
    [chain?.id, setEdges]
  );

  const onEdgeUpdateEnd = useCallback(
    (_, edge) => {
      // delete edge if dropped on graph
      if (!edgeUpdate.toHandle) {
        setEdges((eds) => eds.filter((e) => e.id !== edge.id));
        if (edge.source === "root") {
          api.setRoot(chain.id, { node_id: null });
        } else {
          api.deleteEdge(edge.data.id);
        }
      }
      edgeUpdate.edge = null;
    },
    [chain?.id, setEdges]
  );

  const { callback: debouncedChainUpdate } = useDebounce((...args) => {
    api.updateChain(...args);
  }, 1000);

  const { callback: debouncedChainCreate } = useDebounce((...args) => {
    api.createChain(...args);
  }, 1000);

  const onTitleChange = useCallback(
    (event) => {
      setChain({ ...chain, name: event.target.value });
      if (!chainLoaded) {
        debouncedChainCreate(
          { name: event.target.value, description: "" },
          {
            onSuccess: (response) => {
              navigate(`/chains/${response.data.id}`, {
                replace: true,
              });
              setChain(response.data);
              setChainLoaded(true);
            },
          }
        );
      } else {
        debouncedChainUpdate({
          ...chain,
          name: event.target.value,
        });
      }
    },
    [chain, api, chainLoaded]
  );

  const onSelectionChange = useCallback((selection) => {
    if (selection?.nodes?.length === 0) {
      setSelectedConnector(null);
    }
  }, []);

  return (
    <Box height="93vh">
      <Box pb={1}>
        <Input
          size="sm"
          value={chain?.name || "Unnamed"}
          width={300}
          borderColor="transparent"
          _hover={{
            border: "1px solid",
            borderColor: "gray.500",
          }}
          onChange={onTitleChange}
        />
      </Box>
      <Box ref={reactFlowWrapper} width={"85vw"} height={"100%"}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          isValidConnection={isValidConnection}
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeDragStop={onNodeDragStop}
          onNodesChange={onFilteredNodesChange}
          onEdgesChange={onEdgesChange}
          onEdgeUpdate={onEdgeUpdate}
          onEdgeUpdateStart={onEdgeUpdateStart}
          onEdgeUpdateEnd={onEdgeUpdateEnd}
          onSelectionChange={onSelectionChange}
          nodeTypes={nodeTypes}
          onConnect={onConnect}
          fitView
        >
          <Controls />
          <Background
            color={colorMode === "light" ? "#111" : "#aaa"}
            gap={16}
          />
        </ReactFlow>
      </Box>
    </Box>
  );
};

export default ChainGraphEditor;
