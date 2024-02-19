import React, { useState, useRef, useCallback, useContext } from "react";
import { v4 as uuid4 } from "uuid";
import { Box, IconButton, useToast } from "@chakra-ui/react";
import ReactFlow, {
  addEdge,
  updateEdge,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
} from "reactflow";
import ConfigNode from "chains/flow/ConfigNode";

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
  ChainTypes,
  EdgeState,
  NodeStateContext,
  SelectedNodeContext,
} from "chains/editor/contexts";
import { useConnectionValidator } from "chains/hooks/useConnectionValidator";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRightLeft } from "@fortawesome/free-solid-svg-icons";
import { useRightSidebarContext } from "site/sidebar/context";
import { DirectRootNode } from "chains/flow/DirectRootNode";
import { TabState } from "chains/hooks/useTabState";
import { NOTIFY_SAVED } from "chains/editor/constants";
import { PropEdge } from "chains/PropEdge";
import { LinkEdge } from "chains/LinkEdge";
import { addNode, addType } from "chains/utils";

// Nodes are either a single node or a group of nodes
// ConfigNode renders class_path specific content
const nodeTypes = {
  node: ConfigNode,
  list: ConfigNode,
  root: RootNode,
  direct_root: DirectRootNode,
};

const edgeTypes = {
  PROP: PropEdge,
  LINK: LinkEdge,
};

const getExpectedTypes = (connector) => {
  return Array.isArray(connector?.source_type)
    ? new Set(connector.source_type)
    : new Set([connector.source_type]);
};

const ChainGraphEditor = ({ graph }) => {
  // editor contexts
  const [chain, setChain] = useContext(ChainState);
  const [types, setTypes] = useContext(ChainTypes);
  const nodeState = useContext(NodeStateContext);
  const edgeState = useContext(EdgeState);
  const tabState = useContext(TabState);
  const api = useContext(ChainEditorAPIContext);
  const { selectedNode, selectedConnector, setSelectedConnector } =
    useContext(SelectedNodeContext);

  const reactFlowWrapper = useRef(null);
  const edgeUpdate = useRef(true);
  const { call: loadChain } = useAxios();

  const reactFlowGraph = useGraphForReactFlow(graph, types);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const { colorMode } = useColorMode();

  const toast = useToast();

  // if active chain changes, then reload nodes and edges
  React.useEffect(() => {
    if (reactFlowGraph?.chain !== undefined) {
      setNodes(reactFlowGraph.nodes);
      setEdges(reactFlowGraph.edges);
    }
  }, [reactFlowGraph]);

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
      // first node creates the new chain which must be loaded
      if (chain?.id === undefined) {
        loadChain(`/api/chains/${response.data.chain_id}`, {
          onSuccess: (response) => {
            tabState.setActive((prev) => {
              // update any initial nodes that are missing chain_id
              const nodes = { ...prev.nodes };
              for (const id in nodes) {
                const node = nodes[id];
                if (node.chain_id === null) {
                  nodes[id] = { ...node, chain_id: response.data.id };
                }
              }

              return {
                ...prev,
                chain_id: response.data.id,
                chain: response.data,
                nodes,
              };
            });
            toast({ ...NOTIFY_SAVED, description: "Saved Chain" });
          },
        });
      }
    },
    [chain?.id]
  );

  const onDrop = useCallback(
    async (event) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const incomingData = JSON.parse(
        event.dataTransfer.getData("application/reactflow")
      );

      // data should include either a type or class_path
      // fallback to API if type is not in local state
      let nodeType;
      if (incomingData.type) {
        nodeType = incomingData.type;
      } else if (incomingData.class_path) {
        const { class_path } = incomingData;
        nodeType = types.find((type) => type.class_path === class_path);
        if (!nodeType) {
          const response = await fetch(
            `/api/node_types/?class_path=${class_path}`
          ).then((res) => res.json());
          nodeType = response?.objects?.[0];
        }
      }

      // check if the dropped element is valid
      if (typeof nodeType.type === "undefined" || !nodeType.type) {
        return;
      }

      // target middle-ish of header
      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left - 120,
        y: event.clientY - reactFlowBounds.top - 50,
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
          const style = getEdgeStyle(colorMode);
          flowEdge = {
            id: edgeId,
            source: isOutput ? node.id : newNodeID,
            target: isOutput ? newNodeID : node.id,
            sourceHandle: key === "in" ? "out" : flowNodeType,
            targetHandle: key,
            data: { id: edgeId },
            ...style[key === "in" || key === "out" ? "LINK" : "PROP"],
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
              target_key: flowEdge.targetHandle,
              source_key: flowEdge.sourceHandle,
            };
          }
        }
      }

      // create data object instead of waiting for API
      const data = {
        id: newNodeID,
        chain_id: chain?.id || null,
        class_path: nodeType.class_path,
        node_type_id: nodeType.id,
        name: incomingData.name || "",
        description: incomingData.description || "",
        position: position,
        config: { ...getDefaults(nodeType), ...incomingData.config },
      };

      // add to API, local state, and ReactFlow
      nodeState.setNode(data);
      addType(nodeType, setTypes);
      const flowNode = toReactFlowNode(data, nodeType);
      api.addNode(data, { onSuccess: onNodeSaved });
      setNodes((nds) => nds.concat(flowNode));
      if (edge) {
        data.edges = [edge];
        setEdges((els) => addEdge(flowEdge, els));
        edgeState.setEdge(edge);
      }
      toast({ ...NOTIFY_SAVED, description: "Saved Node" });
    },
    [
      types,
      reactFlowInstance,
      chain?.id,
      selectedNode,
      colorMode,
      selectedConnector,
    ]
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

  const onNodeDragStop = useCallback(
    (event, node) => {
      // ignore position updates for root
      if (node.id === "root") {
        return;
      }

      // update node with new position
      api.updateNodePosition(node.id, node.position);
      const prevNode = nodeState.nodes[node.id];
      nodeState.setNode({ ...prevNode, position: node.position });
    },
    [nodeState.nodes]
  );

  // new edges
  const onConnect = useCallback(
    (params) => {
      // create reactflow edge
      const id = uuid4();
      const source = reactFlowInstance.getNode(params.source);
      const target = reactFlowInstance.getNode(params.target);
      const flowNodeType =
        source.id === "root" ? "root" : source.data.type.type;
      const style = getEdgeStyle(colorMode, flowNodeType);

      // normal LINK and PROP edges
      const from_root =
        source.id === "root" || source.data.type.class_path === "__ROOT__";
      const is_out = params.sourceHandle === "out";
      const is_in = params.targetHandle === "in";
      const from_branch = source.data.type.type === "branch";
      const with_graph =
        source.data.type.type === "graph" ||
        (target.data.type.type === "graph" && params.targetHandle === "loop");

      const displayRelation =
        from_root || is_out || is_in || from_branch || with_graph
          ? "LINK"
          : "PROP";
      setEdges((els) =>
        addEdge({ ...params, ...style[displayRelation], data: { id } }, els)
      );

      // save via API
      if (source.id === "root") {
        // link from root node uses setRoot since it's not stored as an edge
        const root_node_ids = reactFlowInstance
          .getEdges()
          .filter((edge) => edge.source === "root")
          .map((edge) => edge.target);
        root_node_ids.push(params.target);
        api.setRoots(chain.id, { node_ids: root_node_ids });
      } else {
        let relation = "PROP";
        if (with_graph) {
          relation = "GRAPH";
        } else if (from_root || is_out || from_branch) {
          relation = "LINK";
        }

        const data = {
          id,
          source_id: params.source,
          target_id: params.target,
          source_key: params.sourceHandle,
          target_key: params.targetHandle,
          chain_id: chain?.id,
          relation,
        };
        api.addEdge(data);
        edgeState.setEdge(data);
      }
      toast({ ...NOTIFY_SAVED, description: "Saved Edge" });
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
          const root_node_ids = reactFlowInstance
            .getEdges()
            .filter((edge) => edge.source === "root" && edge.id !== oldEdge.id)
            .map((edge) => edge.target);
          root_node_ids.push(newConnection.target);
          api.setRoots(chain.id, { node_ids: root_node_ids });
        }
      } else {
        const isSame =
          oldEdge.source === newConnection.source &&
          oldEdge.target === newConnection.target &&
          oldEdge.sourceHandle === newConnection.sourceHandle &&
          oldEdge.targetHandle === newConnection.targetHandle;
        if (!isSame) {
          toast({ ...NOTIFY_SAVED, description: "Saved Edge" });
          api.updateEdge(oldEdge.data.id, {
            source_id: newConnection.source,
            target_id: newConnection.target,
            source_key: newConnection.sourceHandle,
            target_key: newConnection.targetHandle,
          });
          edgeState.updateEdge(oldEdge.data.id, {
            source_id: newConnection.source,
            target_id: newConnection.target,
            source_key: newConnection.sourceHandle,
            target_key: newConnection.targetHandle,
          });
        }
      }
    },
    [chain?.id, setEdges, reactFlowInstance]
  );

  const onEdgeUpdateEnd = useCallback(
    (_, edge) => {
      // delete edge if dropped on graph
      if (!edgeUpdate.toHandle) {
        setEdges((eds) => eds.filter((e) => e.id !== edge.id));
        edgeState.deleteEdge(edge.data.id);
        if (edge.source === "root") {
          const root_edges = reactFlowInstance
            .getEdges()
            .filter((e) => e.source === "root" && e.id !== edge.id);
          const root_node_ids = root_edges.map((edge) => edge.target);
          api.setRoots(chain.id, { node_ids: root_node_ids });
        } else {
          api.deleteEdge(edge.data.id);
        }
      }
      edgeUpdate.edge = null;
    },
    [chain?.id, setEdges, reactFlowInstance]
  );

  const { callback: debouncedChainUpdate } = useDebounce((...args) => {
    api.updateChain(...args);
  }, 500);

  const { callback: debouncedChainCreate } = useDebounce((...args) => {
    api.createChain(...args);
  }, 800);

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

  const { toggleSidebar } = useRightSidebarContext();
  return (
    <Box height="93vh">
      <Box position="absolute" right={7} display="flex" alignItems="center">
        <IconButton
          ml="auto"
          icon={<FontAwesomeIcon icon={faRightLeft} />}
          onClick={toggleSidebar}
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
          edgeTypes={edgeTypes}
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
