import React from "react";
import { LLM_NAME_MAP } from "chains/constants";

export function llm_name(classPath) {
  if (classPath === undefined) {
    return <i>inherited</i>;
  }

  // lookup LLM name, default to class name if classPath isn't mapped with a label
  return LLM_NAME_MAP[classPath] || classPath.split(".").pop();
}
