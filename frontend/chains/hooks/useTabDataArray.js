import React from "react";
import { useTabDataField } from "chains/hooks/useTabDataField"; // Assuming this is the correct import path

/**
 * Generic hook for managing a tab data field that is an array of objects.
 * Each object in the array has an 'id' and 'chain_id'.
 */
export const useTabDataArray = (tabState, fieldName) => {
  const [items, setItems] = useTabDataField(
    tabState.active,
    tabState.setActive,
    fieldName,
    []
  );

  const setItem = React.useCallback(
    (item) => {
      setItems((prevItems) => {
        const index = prevItems.findIndex(
          (i) => i.id === item.id && i.chain_id === item.chain_id
        );
        if (index > -1) {
          // Update existing item
          return [
            ...prevItems.slice(0, index),
            item,
            ...prevItems.slice(index + 1),
          ];
        } else {
          // Add new item
          return [...prevItems, item];
        }
      });
    },
    [setItems]
  );

  const updateItem = React.useCallback(
    (id, updatedFields) => {
      setItems((prevItems) => {
        const index = prevItems.findIndex((i) => i.id === id);
        if (index > -1) {
          // Update item with the new fields
          const updatedItem = { ...prevItems[index], ...updatedFields };
          return [
            ...prevItems.slice(0, index),
            updatedItem,
            ...prevItems.slice(index + 1),
          ];
        }
        return prevItems;
      });
    },
    [setItems]
  );

  const deleteItem = React.useCallback(
    (itemId) => {
      setItems((prevItems) => prevItems.filter((i) => i.id !== itemId));
    },
    [setItems]
  );

  return {
    items,
    setItems,
    setItem,
    updateItem,
    deleteItem,
  };
};
