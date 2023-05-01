import React, { createContext, useContext, useState, useEffect } from "react";
import { useLazyLoadQuery } from "react-relay/hooks";
import { ChainByIdQuery } from "chains/graphql/ChainByIdQuery";

const ChainContext = createContext();

export const ChainProvider = ({ chainId, children }) => {
  const data = useLazyLoadQuery(ChainByIdQuery, { id: chainId });

  const [chain, setChain] = useState();

  useEffect(() => {
    if (data && data.chain) {
      setChain(data.chain);
    }
  }, [data]);

  return (
    <ChainContext.Provider value={{ chain, setChain }}>
      {children}
    </ChainContext.Provider>
  );
};

export const useChain = () => {
  const context = useContext(ChainContext);
  if (context === undefined) {
    throw new Error("useChain must be used within an ChainProvider");
  }
  return context;
};
