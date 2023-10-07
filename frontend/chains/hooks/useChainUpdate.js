import { useDebounce } from "utils/hooks/useDebounce";
import { useCallback } from "react";
import { useNavigate } from "react-router-dom";

export const useChainUpdate = (chain, setChain, api) => {
  const navigate = useNavigate();
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
              navigate(`/chains/${response.data.id}`, {
                replace: true,
              });
              setChain(response.data);
            },
          }
        );
      } else {
        debouncedChainUpdate({
          ...chain,
          ...data,
        });
      }
    },
    [chain, api]
  );

  return onChainUpdate;
};
