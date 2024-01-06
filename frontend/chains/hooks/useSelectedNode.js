import React, { useCallback, useMemo } from "react";
import { useOnSelectionChange } from "reactflow";
import { useTabDataField } from "chains/hooks/useTabDataField";

/**
 * Hook for a node editor's state. Loads from selected nodes.
 * Also handles syncing back to the ReactFlow node.
 */
export const useNodeEditorState = (selectedNode, nodes, setNode) => {
  const data = selectedNode?.data || {};
  const { type } = data;
  const node = nodes && nodes[selectedNode?.id];

  return useMemo(
    () => ({
      type,
      node,
      setNode,
    }),
    [type, node, setNode]
  );
};

const INITIAL_SELECTION = {
  node: null,
  connector: null,
};

export const useSelectedNode = (tabState) => {
  const [selection, setSelection] = useTabDataField(
    tabState.active,
    tabState.setActive,
    "selection",
    {
      node: null,
      connector: null,
    }
  );

  const setSelectedNode = useCallback(
    (node) => {
      setSelection((prev) => ({ ...(prev || INITIAL_SELECTION), node: node }));
    },
    [setSelection]
  );

  const setSelectedConnector = useCallback(
    (connector) => {
      setSelection((prev) => ({
        ...(prev || INITIAL_SELECTION),
        connector: connector,
      }));
    },
    [setSelection]
  );

  useOnSelectionChange({
    onChange: ({ nodes }) => {
      setSelection((prev) => ({
        ...(prev || INITIAL_SELECTION),
        node: nodes[0] || null,
      }));
    },
  });

  return useMemo(
    () => ({
      selectedNode: selection.node,
      selectedConnector: selection.connector,
      setSelectedNode,
      setSelectedConnector,
    }),
    [selection, setSelectedNode, setSelectedConnector]
  );
};
