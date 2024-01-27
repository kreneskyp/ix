import React from "react";
import { useTabDataArray } from "chains/hooks/useTabDataArray";

/**
 * Hook for managing edge state in a specific tab.
 * Each edge in the array has an 'id' and 'chain_id'.
 */
export const useEdgeState = (tabState) => {
  const {
    items: edges,
    setItems: setEdges,
    setItem: setEdge,
    updateItem: updateEdge,
    deleteItem: deleteEdge,
  } = useTabDataArray(tabState, "edges");

  return {
    edges, // Current array of edges
    setEdges, // Function to set the entire edges array
    setEdge, // Function to update or add a single edge
    updateEdge, // Function to update a single edge by id and chain_id
    deleteEdge, // Function to delete a specific edge by id and chain_id
  };
};
