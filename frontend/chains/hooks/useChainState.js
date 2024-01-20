import React from "react";
import { useTabDataField } from "chains/hooks/useTabDataField";

/**
 * Central state for chains in the editor. All components that need to
 * read or write chain state should use this hook.
 */
export const useChainState = (tabState) => {
  const [chain, _setChain] = useTabDataField(
    tabState.active,
    tabState.setActive,
    "chain",
    {}
  );

  const setChain = React.useCallback(
    (updatedChain) => {
      _setChain(updatedChain);

      // new chain needs chain_id set up
      if (
        updatedChain.id !== undefined &&
        tabState?.active?.chain_id === null
      ) {
        tabState.setActive((prev) => ({
          ...prev,
          chain_id: updatedChain.id,
        }));
      }
    },
    [tabState?.active, _setChain]
  );

  return React.useMemo(() => [chain, setChain], [chain, setChain]);
};
