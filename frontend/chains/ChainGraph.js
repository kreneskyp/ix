import React, { useState, useEffect } from "react";
import ReactFlow, { Background, Controls } from "reactflow";
import dagre from "dagre";
import "reactflow/dist/style.css";
import { Box } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/color-mode";
import "./styles.css";
import ChainNode from "chains/flow/ChainNode";
import GroupNode from "chains/flow/GroupNode";

const nodeTypes = {
  chain: ChainNode,
  container: GroupNode,
};

export const ChainGraph = ({ graph }) => {
  const [elements, setElements] = useState([]);
  const { colorMode } = useColorMode();

  if (graph === null) {
    return null;
  }

  const edgeStyle = {
    stroke: colorMode === "light" ? "#000" : "#FFF",
    strokeWidth: 2,
    strokeLinecap: "round",
    strokeDasharray: "4, 4",
    strokeDashoffset: 0,
    animation: "dash 1s linear infinite",
  };

  const createDagreGraph = (nodes, edges) => {
    const seen = new Set();
    const g = new dagre.graphlib.Graph();
    g.setGraph({ rankdir: "LR" });
    g.setDefaultEdgeLabel(() => ({}));

    nodes.forEach((node) => {
      let width;
      if (node.type === "container") {
        width = (node.data.children.length - 1) * 250 + 270;
      } else {
        width = 250;
      }
      g.setNode(node.id, { label: node.data.label, width, height: 200 });
      seen.add(node.id);
    });

    // add edges for nodes that were seen.
    // this allows a single edges list to be used for both the
    // top level dagre and container dagres
    edges.forEach((edge) => {
      if (seen.has(edge.source) && seen.has(edge.target)) {
        g.setEdge(edge.source, edge.target);
      }
    });

    dagre.layout(g);

    return g;
  };

  useEffect(() => {
    const nodesData = [];
    const edgesData = [];
    const containers = [];
    const flowNodes = {};

    const nodeMap = {
      [graph.chain.root.id]: graph.chain.root,
      ...Object.fromEntries(graph.nodes.map((node) => [node.id, node])),
    };

    const processNode = (node) => {
      if (node.id in flowNodes) {
        return;
      }

      if (node.parent && !node.parent.id in flowNodes) {
        processNode(nodeMap[node.parent.id]);
      }

      let nodeType = "chain";
      if (node.nodeType === "LIST") {
        nodeType = "container";
        containers.push(node.id);
      }

      const nodeData = {
        id: node.id,
        type: nodeType,
        data: { node, children: [] },
        parent: node.parent?.id,
        extent: node.parent?.id === null ? "parent" : null,
      };

      if (node.parent?.id !== undefined) {
        nodeData.extent = "parent";
        nodeData.parentNode = node.parent.id;
        nodeData.position = { x: 10, y: 10 };
        flowNodes[node.parent.id].data.children.push(node.id);
      }

      flowNodes[node.id] = nodeData;
      nodesData.push(nodeData);
      return node;
    };

    processNode(graph.chain.root);
    graph.nodes.forEach((node) => {
      if (flowNodes[node.id] === undefined) {
        processNode(node);
      }
    });

    graph.edges.forEach((edge) => {
      // Add all edges, excluding edges between a parent and child
      // the parent-child relationship is only implicitly shown
      if (nodeMap[edge.target.id].parent?.id !== edge.source.id) {
        edgesData.push({
          id: edge.id,
          type: "default",
          source: edge.source.id,
          target: edge.target.id,
          sourceHandle: edge.source_key,
          targetHandle: edge.target_key,
          style: edgeStyle,
        });
      }
    });

    // auto-arrange top level elements
    const dagreGraph = createDagreGraph(nodesData, edgesData);
    const newNodes = nodesData.map((node) => {
      const position = dagreGraph.node(node.id);

      if (node.parent !== undefined) {
        return node;
      }

      return {
        ...node,
        position: { x: position.x, y: position.y },
      };
    });

    // arrange elements within containers
    for (const id of containers) {
      const containerNode = flowNodes[id];
      const childNodes = containerNode.data.children.map((id) => flowNodes[id]);
      const dagreGraph = createDagreGraph(childNodes, edgesData);

      for (const childNode of childNodes) {
        const dagrePosition = dagreGraph.node(childNode.id);

        // dagre always adds width/2 and height/2 to x and y. Child nodes are
        // relative to the container. Adjust spacing so that it is closer to the origin
        childNode.position = {
          x: dagrePosition.x - 115,
          y: dagrePosition.y - 60,
        };
      }
    }

    setElements({ nodes: newNodes, edges: edgesData });
  }, [graph, colorMode]);

  return (
    <Box height={1000} width={1500}>
      <ReactFlow {...elements} nodeTypes={nodeTypes} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </Box>
  );
};

export default ChainGraph;
