import { useContext, useMemo } from "react";
import { SelectedNodeContext } from "chains/editor/contexts";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import { useDebounce } from "utils/hooks/useDebounce";

/**
 * Hook for a node editor's API. Returns debounced updateNode functions
 * for the full object and for individual fields.
 */
export const useNodeEditorAPI = (node, setNode) => {
  const { selectedNode } = useContext(SelectedNodeContext);
  const api = useContext(ChainEditorAPIContext);
  const { callback: debouncedUpdateNode } = useDebounce(api.updateNode, 500);
  const handleConfigChange = useMemo(() => {
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

    const field = (key, value, delay = 500) => {
      config({ ...node.config, [key]: value }, delay);
    };

    return { all, field, config };
  }, [selectedNode, api, node, setNode]);

  return { handleConfigChange };
};
