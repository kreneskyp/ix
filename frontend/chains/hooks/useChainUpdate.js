import { useToast } from "@chakra-ui/react";
import { useCallback } from "react";
import { useDebounce } from "utils/hooks/useDebounce";
import { NOTIFY_SAVED } from "chains/editor/constants";

export const useChainUpdate = (chain, setChain, api) => {
  const toast = useToast();
  const { callback: debouncedChainUpdate } = useDebounce((...args) => {
    api.updateChain(...args).then((response) => {
      const name = response.data.name || "chain";
      toast({
        ...NOTIFY_SAVED,
        title: "Chain saved",
        description: `saved ${name}`,
      });
    });
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
              const name = response.data.name || "new chain";
              toast({
                ...NOTIFY_SAVED,
                title: "Chain created",
                description: `created ${name}`,
              });
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
