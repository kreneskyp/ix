import React, {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useOnSelectionChange } from "reactflow";

/**
 * Hook for a node editor's state. Loads from selected nodes.
 * Also handles syncing back to the ReactFlow node.
 */
export const useNodeEditorState = (selectedNode, nodes, setNode) => {
  const data = selectedNode?.data || {};
  const { type } = data;
  const node = nodes && nodes[selectedNode?.id];

  const onUpdateNode = useCallback(
    (data) => {
      setNode(data);
    },
    [selectedNode, setNode]
  );

  return useMemo(
    () => ({
      type,
      node,
      setNode: onUpdateNode,
    }),
    [type, node, onUpdateNode]
  );
};

export const useSelectedNode = () => {
  const [data, setData] = useState({
    selectedNode: null,
    selectedConnector: null,
  });

  const setSelectedNode = useCallback(
    (node) => {
      setData((prev) => ({ ...prev, selectedNode: node }));
    },
    [setData]
  );

  const setSelectedConnector = useCallback(
    (connector) => {
      setData((prev) => ({ ...prev, selectedConnector: connector }));
    },
    [setData]
  );

  const onSelectionChange = useOnSelectionChange({
    onChange: ({ nodes }) => {
      setData((prev) => ({
        ...prev,
        selectedNode: nodes[0] || null,
        selectedConfig: nodes[0]?.data?.node?.config || null,
      }));
    },
  });

  return {
    ...data,
    setSelectedNode,
    setSelectedConnector,
    setConfig,
    onSelectionChange,
  };
};
