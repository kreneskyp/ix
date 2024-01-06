import React from "react";

export const TabState = React.createContext(null);

export const useTabState = (initial) => {
  const [index, setIndex] = React.useState(0);
  const [state, setState] = React.useState(initial || []);

  const removeTab = React.useCallback(
    (toRemove) => {
      if (state.length === 1) {
        return;
      } else if (toRemove === index) {
        if (state.length - 1 <= toRemove) {
          setIndex(index - 1);
        }
      } else if (toRemove < index) {
        setIndex(index - 1);
      }

      const close = () => {
        setState((prev) => prev.filter((tab, i) => i !== toRemove));
      };

      // very small timeout to allow index to change before removing tab
      // hacky way around a race condition where active tab alters state
      // after the tab is removed. Timeout allows handlers to clear.
      setTimeout(close, 50);
    },
    [state, index]
  );

  const addTab = React.useCallback(
    (tab) => {
      setState((prev) => [...prev, tab]);
      setIndex(state.length);
    },
    [state]
  );

  const active = state[index];

  const setActive = React.useCallback(
    (value) => {
      setState((prev) => {
        const newState = [...prev];
        newState[index] =
          typeof value === "function" ? value(prev[index]) : value;
        return newState;
      });
    },
    [index]
  );

  return {
    active,
    setActive,
    index,
    setIndex,
    state,
    setState,
    removeTab,
    addTab,
  };
};
