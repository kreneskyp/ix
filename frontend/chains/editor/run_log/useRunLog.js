import React from "react";
import { RunLog } from "chains/editor/contexts";

export const useRunLog = () => {
  return React.useContext(RunLog);
};
