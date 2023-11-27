import { useMemo } from "react";
import { useColorMode } from "@chakra-ui/color-mode";

export const getEdgeStyle = (colorMode) => {
  const linkColor = colorMode === "light" ? "black" : "white";
  const propColor = colorMode === "light" ? "#888" : "#666";

  return {
    LINK: {
      type: "smoothstep",
      markerEnd: { type: "arrowclosed", color: linkColor },
      style: {
        stroke: linkColor,
        strokeWidth: 2,
        strokeLinecap: "round",
      },
    },
    PROP: {
      type: "smoothstep",
      markerEnd: { type: "arrowclosed", color: propColor },
      style: {
        stroke: propColor,
        strokeWidth: 2,
        strokeLinecap: "round",
      },
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

    const edgeStyle = getEdgeStyle(colorMode, "chain");
    const defaultEdgeStyle = edgeStyle.LINK;

    const edges =
      graph?.edges?.map((edge) => {
        const sourceType = nodeTypes[nodeMap[edge.source_id].node_type_id].type;
        return {
          id: edge.id,
          source: edge.source_id,
          target: edge.target_id,
          sourceHandle: edge.source_key,
          targetHandle: edge.target_key,
          ...(edgeStyle[edge.relation] || defaultEdgeStyle),
          data: {
            id: edge.id,
          },
        };
      }) || [];

    // Deprecated direct roots: support for chains that haven't converted to the
    // new root node type.
    const hasDirectRoot = roots?.find((root) => root.class_path !== "__ROOT__");
    if (hasDirectRoot) {
      // Push static root and add an edge if a root node exists
      nodes.push({
        id: "root",
        type: "direct_root",
        position: { x: 100, y: 300 },
      });
      roots?.map((root, i) => {
        edges.push({
          id: `root_connector_${i}`,
          source: "root",
          target: root.id,
          sourceHandle: "out",
          targetHandle: "in",
          ...defaultEdgeStyle,
        });
      });
    }

    return { chain: graph?.chain, nodes, edges, root };
  }, [graph?.chain?.id, colorMode]);
};
