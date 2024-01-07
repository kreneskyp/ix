import React from "react";

/** Use a field in a tab's state. Routes requests to the active tab.
 *
 * Use this hook to access a top-level field in a tab's state dict. This
 * hook is intended to create more specific setters and getters that
 * always point to the active tab.
 * **/
export const useTabDataField = (data, setData, key, initial) => {
  const set = React.useCallback(
    (value) => {
      setData((prev) => {
        const newValue =
          typeof value === "function" ? value((prev || {})[key]) : value;
        return { ...prev, [key]: newValue };
      });
    },
    [key, setData]
  );

  const value = data !== undefined ? data[key] : undefined;
  return [value === undefined ? initial : value, set];
};
