import { useDebounce } from "utils/hooks/useDebounce";
import { useCallback } from "react";

export const useChainUpdate = (chain, setChain, api) => {
  const { callback: debouncedChainUpdate } = useDebounce((...args) => {
    api.updateChain(...args);
  }, 500);

  const { callback: debouncedChainCreate } = useDebounce((...args) => {
    api.createChain(...args);
  }, 800);

  const onChainUpdate = useCallback(
    (data) => {
      setChain(data);
      if (chain?.id === undefined) {
        debouncedChainCreate(
          { name: "", description: "", ...data },
          {
            onSuccess: (response) => {
              setChain(response.data);
            },
          }
        );
      } else {
        debouncedChainUpdate(chain.id, {
          ...chain,
          ...data,
        });
      }
    },
    [chain, api]
  );

  return onChainUpdate;
};
