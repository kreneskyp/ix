import React, { useState, useRef, useCallback, useContext } from "react";
import { v4 as uuid4 } from "uuid";
import { Box, IconButton, Input } from "@chakra-ui/react";
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
import { getDefaults } from "json_form/JSONSchemaForm";
import { useDebounce } from "utils/hooks/useDebounce";
import { useAxios } from "utils/hooks/useAxios";
import {
  ChainState,
  NodeStateContext,
  SelectedNodeContext,
} from "chains/editor/contexts";
import { useConnectionValidator } from "chains/hooks/useConnectionValidator";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRightLeft } from "@fortawesome/free-solid-svg-icons";
import { useChainUpdate } from "chains/hooks/useChainUpdate";

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

const ChainGraphEditor = ({ graph, rightSidebarDisclosure }) => {
  const reactFlowWrapper = useRef(null);
  const edgeUpdate = useRef(true);
  const { call: loadChain } = useAxios();
  const { chain, setChain } = useContext(ChainState);

  const reactFlowGraph = useGraphForReactFlow(graph);
  const [nodes, setNodes, onNodesChange] = useNodesState(reactFlowGraph.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(reactFlowGraph.edges);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const { colorMode } = useColorMode();
  const navigate = useNavigate();
  const nodeState = useContext(NodeStateContext);
  const api = useContext(ChainEditorAPIContext);
  const { selectedNode, selectedConnector, setSelectedConnector } =
    useContext(SelectedNodeContext);

  // handle dragging a node onto the graph
  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  // rebuild edges if colorMode toggles
  React.useEffect(() => {
    setEdges(reactFlowGraph.edges);
  }, [colorMode]);

  const onNodeSaved = useCallback(
    (response) => {
      // first node creates the new chain
      // redirect to the correct URL
      if (chain?.id === undefined) {
        navigate(`/chains/${response.data.chain_id}`, { replace: true });
        loadChain(`/api/chains/${response.data.chain_id}`, {
          onSuccess: (response) => {
            setChain(response.data);
          },
        });
      }
    },
    [chain?.id]
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
      let flowEdge = null;
      let edgeConnector = null;
      if (selectedNode || selectedConnector) {
        // selectedConnector has all properties but fallback to selectedNode if it doesn't
        const node = selectedConnector?.node || selectedNode?.data.node;
        const selectedType = selectedConnector?.type || selectedNode?.data.type;

        if (selectedConnector) {
          edgeConnector = selectedConnector.connector;
        } else {
          // Only Node selected:
          // select the first open connector accepting the node type
          const targetType = selectedNode.data.type;
          edgeConnector = targetType.connectors?.find((connector) =>
            getExpectedTypes(connector).has(nodeType.type)
          );
        }

        if (edgeConnector) {
          // output connector is a source, flip the edge
          const isOutput = edgeConnector.key === "out";
          const key = isOutput ? "in" : edgeConnector.key;

          // create flow edge to validate and add to ReactFlow
          const edgeId = uuid4();
          const flowNodeType = nodeType.type;
          const style = getEdgeStyle(colorMode, flowNodeType);
          flowEdge = {
            id: edgeId,
            source: isOutput ? node.id : newNodeID,
            target: isOutput ? newNodeID : node.id,
            sourceHandle: key === "in" ? "out" : flowNodeType,
            targetHandle: key,
            data: { id: edgeId },
            ...style,
          };

          // validate flowEdge before creating datum for API
          const sourceType =
            flowEdge.source === newNodeID ? nodeType : selectedType;
          const targetType =
            flowEdge.target === newNodeID ? nodeType : selectedType;
          if (isValidConnection({ ...flowEdge, sourceType, targetType })) {
            edge = {
              id: edgeId,
              source_id: flowEdge.source,
              target_id: flowEdge.target,
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
        name: "",
        description: "",
        position: position,
        config: getDefaults(nodeType),
      };
      if (edge) {
        data.edges = [edge];
      }
      nodeState.setNode(data);

      // create ReactFlow node
      const flowNode = toReactFlowNode(data, nodeType);

      // add to API and ReactFlow
      api.addNode(data, { onSuccess: onNodeSaved });
      setNodes((nds) => nds.concat(flowNode));

      if (edge) {
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
    // ignore position updates for root
    if (node.id === "root") {
      return;
    }

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
      setEdges((els) => addEdge({ ...params, ...style, data: { id } }, els));

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

  const { isValidConnection } = useConnectionValidator(edgeUpdate);

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
  }, 500);

  const { callback: debouncedChainCreate } = useDebounce((...args) => {
    api.createChain(...args);
  }, 800);

  const onChainUpdate = useChainUpdate(chain, setChain, api);
  const onTitleChange = useCallback(
    (event) => {
      onChainUpdate({ ...chain, name: event.target.value });
    },
    [chain, onChainUpdate]
  );

  const onSelectionChange = useCallback((selection) => {
    if (selection?.nodes?.length === 0) {
      setSelectedConnector(null);
    }
  }, []);

  // New chains need a specific viewport because fitview
  // centers the root node.
  const displayProps = React.useMemo(() => {
    if (graph?.chain?.id) {
      return {
        fitView: true,
        fitViewOptions: {
          minZoom: 0,
          maxZoom: 1,
        },
      };
    } else {
      return {
        defaultViewport: {
          x: 0,
          y: 0,
          zoom: 1,
        },
      };
    }
  }, [graph?.chain?.id]);

  return (
    <Box height="93vh">
      <Box display="flex" alignItems="center">
        <Box pb={1}>
          <Input
            size="sm"
            placeholder={"Unnamed Chain"}
            value={chain?.name || ""}
            width={300}
            borderColor="transparent"
            _hover={{
              border: "1px solid",
              borderColor: "gray.500",
            }}
            onChange={onTitleChange}
          />
        </Box>

        <IconButton
          ml="auto"
          icon={<FontAwesomeIcon icon={faRightLeft} />}
          onClick={rightSidebarDisclosure.onOpen}
          aria-label="Open Sidebar"
          title={"Open Sidebar"}
        />
      </Box>
      <Box ref={reactFlowWrapper} width={"calc(100vw - 100px)"} height={"100%"}>
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
          {...displayProps}
          snapToGrid={true}
          snapGrid={[10, 10]}
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
