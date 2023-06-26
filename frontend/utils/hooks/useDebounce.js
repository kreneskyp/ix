import { useCallback, useEffect, useRef } from "react";

// helper for debouncing a function. Used to delay
// updates triggered by rapid fire events such as typing.
export const useDebounce = (fn, ms = 0) => {
  const timeout = useRef(null);

  const clear = useCallback(() => {
    if (timeout.current) {
      clearTimeout(timeout.current);
      timeout.current = null;
    }
  }, [fn]);

  const callback = useCallback(
    (...args) => {
      clear();
      timeout.current = setTimeout(fn, ms, ...args);
    },
    [fn]
  );

  return { callback, clear };
};
