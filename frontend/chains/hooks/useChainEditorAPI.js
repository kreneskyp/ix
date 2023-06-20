import { useChainEditorMutation } from "chains/hooks/useChainEditorMutation";
import { UpdateChainMutation } from "chains/graphql/UpdateChainMutation";
import { AddChainEdgeMutation } from "chains/graphql/AddChainEdgeMutation";
import { UpdateChainNodeMutation } from "chains/graphql/UpdateChainNodeMutation";
import { DeleteChainNodeMutation } from "chains/graphql/DeleteChainNodeMutation";
import { UpdateChainEdgeMutation } from "chains/graphql/UpdateChainEdgeMutation";
import { DeleteChainEdgeMutation } from "chains/graphql/DeleteChainEdgeMutation";
import { AddChainNodeMutation } from "chains/graphql/AddChainNodeMutation";
import { useCallback, useMemo } from "react";
import { SetChainRootMutation } from "chains/graphql/SetChainRootMutation";

// utility for wrapping default onCompleted with onCompleted arg
const useNestedCallback = (func, callback) => {
  return (response, errors) => {
    func(response, errors);
    if (callback) {
      callback(response, errors);
    }
  };
};

export const useChainEditorAPI = ({
  chain,
  onCompleted,
  onError,
  reactFlowInstance,
}) => {
  const { setNodes, setEdges } = reactFlowInstance ? reactFlowInstance : {};

  const { callback: updateChain, isInFlight: updateChainInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: UpdateChainMutation,
      reactFlowInstance,
    });
  const { callback: setRoot, isInFlight: setRootInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: SetChainRootMutation,
      reactFlowInstance,
    });
  const { callback: addNode, isInFlight: addNodeInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: AddChainNodeMutation,
      reactFlowInstance,
    });
  const { callback: updateNode, isInFlight: updateNodeInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: UpdateChainNodeMutation,
      reactFlowInstance,
    });

  const { callback: deleteNode, isInFlight: deleteNodeInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: DeleteChainNodeMutation,
      reactFlowInstance,
    });
  const { callback: addEdge, isInFlight: addEdgeInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: AddChainEdgeMutation,
      reactFlowInstance,
    });
  const { callback: updateEdge, isInFlight: updateEdgeInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: UpdateChainEdgeMutation,
      reactFlowInstance,
    });
  const { callback: deleteEdge, isInFlight: deleteEdgeInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: DeleteChainEdgeMutation,
      reactFlowInstance,
    });

  return useMemo(() => {
    // aggregate inFlight status
    const isInFlight =
      updateChainInFlight ||
      setRootInFlight ||
      addNodeInFlight ||
      updateNodeInFlight ||
      deleteNodeInFlight ||
      addEdgeInFlight ||
      updateEdgeInFlight ||
      deleteEdgeInFlight;

    return {
      isInFlight,
      updateChain,
      setRoot,
      updateNode,
      addNode,
      addEdge,
      updateEdge,
      deleteEdge,
    };
  }, [chain?.id, onCompleted, onError, reactFlowInstance]);
};
