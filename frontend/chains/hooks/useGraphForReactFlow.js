import { useMemo } from "react";
import { useColorMode } from "@chakra-ui/color-mode";

export const getEdgeStyle = (colorMode, type) => {
  const color = colorMode === "light" ? "black" : "white";
  return {
    type: "smoothstep",
    markerEnd: { type: "arrowclosed", color },
    style: {
      stroke: color,
      strokeWidth: 2,
      strokeLinecap: "round",
    },
  };
};

export const toReactFlowNode = (node, nodeType) => {
  return {
    id: node.id,
    type: nodeType.display_type,
    position: node.position,
    data: {
      type: nodeType,
      node,
    },
  };
};

/**
 * Convert the graphql graph to a react flow graph objects.
 * Including adding static root node.
 */
export const useGraphForReactFlow = (graph) => {
  const { colorMode } = useColorMode();

  const nodeTypes = useMemo(() => {
    const nodeTypes = {};
    graph?.types?.forEach((type) => {
      nodeTypes[type.id] = type;
    });
    return nodeTypes;
  }, [graph]);

  return useMemo(() => {
    const nodeMap = {};
    graph?.nodes?.forEach((node) => {
      nodeMap[node.id] = node;
    });

    const roots = graph?.nodes?.filter((node) => node.root);
    const nodes =
      graph?.nodes?.map((node) => {
        return toReactFlowNode(node, nodeTypes[node.node_type_id]);
      }) || [];

    const chainPropEdgeStyle = getEdgeStyle(colorMode, "chain");
    const defaultEdgeStyle = getEdgeStyle(colorMode);

    const edges =
      graph?.edges?.map((edge) => {
        const sourceType = nodeTypes[nodeMap[edge.source_id].node_type_id].type;
        return {
          id: edge.id,
          source: edge.source_id,
          target: edge.target_id,
          sourceHandle: edge.relation === "PROP" ? sourceType : "out",
          targetHandle: edge.relation === "PROP" ? edge.key : "in",
          ...(sourceType === "chain" ? chainPropEdgeStyle : defaultEdgeStyle),
          data: {
            id: edge.id,
          },
        };
      }) || [];

    // Push static root and add an edge if a root node exists
    nodes.push({
      id: "root",
      type: "root",
      position: { x: 100, y: 300 },
    });
    roots.map((root, i) => {
      edges.push({
        id: `root_connector_${i}`,
        source: "root",
        target: root.id,
        sourceHandle: "out",
        targetHandle: "in",
        ...defaultEdgeStyle,
      });
    });

    return { chain: graph?.chain, nodes, edges, root };
  }, [graph?.chain?.id, colorMode]);
};
