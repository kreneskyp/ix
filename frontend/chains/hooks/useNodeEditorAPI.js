import React from "react";
import { useToast } from "@chakra-ui/react";
import { SelectedNodeContext } from "chains/editor/contexts";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import { useDebounce } from "utils/hooks/useDebounce";
import { NOTIFY_SAVED } from "chains/editor/constants";

/**
 * Hook for a node editor's API. Returns debounced updateNode functions
 * for the full object and for individual fields.
 */
export const useNodeEditorAPI = (node, setNode) => {
  const { selectedNode } = React.useContext(SelectedNodeContext);
  const api = React.useContext(ChainEditorAPIContext);
  const updateNode = React.useCallback(
    (...args) => {
      api.updateNode(...args).then((response) => {
        const node = response.data;
        const name = node.name || node.class_path.split(".").pop();
        toast({
          ...NOTIFY_SAVED,
          description: `Saved ${name}`,
        });
      });
    },
    [api.updateNode]
  );

  const { callback: debouncedUpdateNode } = useDebounce(updateNode, 800);
  const toast = useToast();
  const handleConfigChange = React.useMemo(() => {
    function all(newNode, delay = 0) {
      const data = {
        name: newNode.name,
        description: newNode.description,
        config: newNode.config,
        class_path: node.class_path,
        position: node.position,
      };
      debouncedUpdateNode(node.id, data);
      setNode(newNode);
    }

    const config = (newConfig, delay = 500) => {
      all({ ...node, config: newConfig }, delay);
    };

    const fields = (newFields, delay = 500) => {
      config({ ...node.config, ...newFields }, delay);
    };

    const field = (key, value, delay = 500) => {
      config({ ...node.config, [key]: value }, delay);
    };

    return { all, field, fields, config };
  }, [selectedNode, api, node, setNode]);

  return { handleConfigChange };
};
