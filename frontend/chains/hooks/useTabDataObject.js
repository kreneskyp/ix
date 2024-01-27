import React from "react";
import { useTabDataField } from "chains/hooks/useTabDataField";

/**
 * Generic hook for managing a property that is an object mapping id to item.
 */
export const useTabDataObject = (tabState, fieldName, initialValue) => {
  const [items, setItems] = useTabDataField(
    tabState.active,
    tabState.setActive,
    fieldName,
    initialValue
  );

  const setItem = React.useCallback(
    (item) => {
      setItems((prevItems) => {
        // Reject updates from other tabs to prevent data corruption
        if (item.chain_id !== tabState.active.chain_id) {
          return prevItems;
        }
        return { ...prevItems, [item.id]: item };
      });
    },
    [tabState?.active?.chain_id, setItems]
  );

  const deleteItem = React.useCallback(
    (itemId) => {
      setItems((prevItems) => {
        const newItems = { ...prevItems };
        delete newItems[itemId];
        return newItems;
      });
    },
    [setItems]
  );

  return {
    items,
    setItems,
    setItem,
    deleteItem,
  };
};
