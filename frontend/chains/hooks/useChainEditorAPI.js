import { useChainEditorMutation } from "chains/hooks/useChainEditorMutation";
import { UpdateChainMutation } from "chains/graphql/UpdateChainMutation";
import { AddChainEdgeMutation } from "chains/graphql/AddChainEdgeMutation";
import { UpdateChainNodeMutation } from "chains/graphql/UpdateChainNodeMutation";
import { DeleteChainNodeMutation } from "chains/graphql/DeleteChainNodeMutation";
import { UpdateChainEdgeMutation } from "chains/graphql/UpdateChainEdgeMutation";
import { DeleteChainEdgeMutation } from "chains/graphql/DeleteChainEdgeMutation";
import { AddChainNodeMutation } from "chains/graphql/AddChainNodeMutation";

export const useChainEditorAPI = ({ chain, onCompleted, onError }) => {
  const { callback: updateChain, isInFlight: updateChainInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: UpdateChainMutation,
    });
  const { callback: addNode, isInFlight: addNodeInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: AddChainNodeMutation,
    });
  const { callback: updateNode, isInFlight: updateNodeInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: UpdateChainNodeMutation,
    });
  const { callback: deleteNode, isInFlight: deleteNodeInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: DeleteChainNodeMutation,
    });
  const { callback: addEdge, isInFlight: addEdgeInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: AddChainEdgeMutation,
    });
  const { callback: updateEdge, isInFlight: updateEdgeInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      query: UpdateChainEdgeMutation,
    });
  const { callback: deleteEdge, isInFlight: deleteEdgeInFlight } =
    useChainEditorMutation({
      chain,
      onCompleted,
      onError,
      mutation: DeleteChainEdgeMutation,
    });

  // aggregate inFlight status
  const isInFlight =
    updateChainInFlight ||
    addNodeInFlight ||
    updateNodeInFlight ||
    deleteNodeInFlight ||
    addEdgeInFlight ||
    updateEdgeInFlight ||
    deleteEdgeInFlight;

  return {
    isInFlight,
    updateNode,
    addNode,
    deleteNode,
    addEdge,
    updateEdge,
    deleteEdge,
  };
};
