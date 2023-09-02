import { useEffect, useMemo, useState } from "react";

export const useChainState = (graph) => {
  const [chain, setChain] = useState(graph?.chain);

  // update chain if graph changes
  useEffect(() => {
    console.log("graph changed, chain=", graph?.chain);
    setChain(graph?.chain);
  }, [graph?.chain]);

  return useMemo(
    () => ({
      chain,
      setChain,
    }),
    [chain, setChain]
  );
};
