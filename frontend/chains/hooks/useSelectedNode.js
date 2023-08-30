import React, { useCallback, useState } from "react";
import { useOnSelectionChange } from "reactflow";

export const useSelectedNode = () => {
  const [data, setData] = useState({
    selectedNode: null,
    selectedConnector: null,
    config: null,
  });

  const setSelectedNode = useCallback(
    (node) => {
      setData((prev) => ({ ...prev, selectedNode: node }));
    },
    [setData]
  );

  const setConfig = useCallback(
    (config) => {
      setData((prev) => ({ ...prev, config }));
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
