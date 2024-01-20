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
      setNodes((prev) => {
        // HAX: reject updates from other tabs. This protects against hooks that
        // aren't updating correctly when switching tabs. This only treats the
        // symptom, not the cause. But it prevents data corruption of nodes
        // leaking to other tabs.
        if (node.chain_id !== tabState.active.chain_id) {
          return prev;
        }
        return { ...prev, [node.id]: node };
      });
    },
    [tabState?.active?.chain_id, setNodes]
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
