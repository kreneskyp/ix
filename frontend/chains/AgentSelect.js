import React from "react";

import { ChainSelect } from "chains/ChainSelect";

export const AgentSelect = ({ onChange, value }) => {
  return <ChainSelect onChange={onChange} value={value} is_agent={true} />;
};
