import { useTabDataObject } from "chains/hooks/useTabDataObject";

/**
 * Central state for nodes in the editor. All components that need to
 * read or write node state should use this hook.
 */
export const useNodeState = (tabState) => {
  const {
    items: nodes,
    setItems: setNodes,
    setItem: setNode,
    deleteItem: deleteNode,
  } = useTabDataObject(tabState, "nodes");

  return {
    nodes,
    setNodes,
    setNode,
    deleteNode,
  };
};
