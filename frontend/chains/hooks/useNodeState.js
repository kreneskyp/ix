import { useCallback, useEffect, useMemo, useState } from "react";

/**
 * Central state for nodes in the editor. All components that need to
 * read or write node state should use this hook.
 */
export const useNodeState = (chain, initialNodes) => {
  const [nodes, setNodes] = useState(initialNodes || {});

  // convert node list into a map, reload if the chain changes
  // first render chain may be null.
  useEffect(() => {
    const nodeMap = {};
    initialNodes?.forEach((node) => {
      nodeMap[node.id] = node;
    });
    setNodes(nodeMap);
  }, [chain?.id]);

  // callback for updating a single node
  const setNode = useCallback(
    (node) => {
      setNodes((prev) => ({ ...prev, [node.id]: node }));
    },
    [setNodes]
  );

  return useMemo(
    () => ({
      nodes,
      setNodes,
      setNode,
    }),
    [nodes, setNodes, setNode]
  );
};
