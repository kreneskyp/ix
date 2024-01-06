import React from "react";
import { useTabDataField } from "chains/hooks/useTabDataField";

/**
 * Central state for nodes in the editor. All components that need to
 * read or write node state should use this hook.
 */
export const useNodeState = (tabState) => {
  const [nodes, setNodes] = useTabDataField(
    tabState.active,
    tabState.setActive,
    "nodes",
    {
      node: null,
      connector: null,
    }
  );

  const setNode = React.useCallback(
    (node) => {
      setNodes((prev) => ({ ...prev, [node.id]: node }));
    },
    [setNodes]
  );

  return React.useMemo(
    () => ({
      nodes,
      setNodes,
      setNode,
    }),
    [nodes, setNodes, setNode]
  );
};
