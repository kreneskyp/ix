import React from "react";
import { Box } from "@chakra-ui/react";
import { ExecutionStatusIcon } from "chains/editor/run_log/icons";
import { RunLog } from "chains/editor/contexts";

export const NodeExecutionIcon = ({ node }) => {
  const run_log = React.useContext(RunLog);
  const execution = run_log.log_by_node[node?.id];

  const onClick = React.useCallback(() => {
    run_log.setExecution(execution);
    run_log.disclosure.onOpen();
  }, [execution]);

  if (!execution) {
    return null;
  }

  return (
    <Box cursor={"pointer"} onClick={onClick}>
      <ExecutionStatusIcon execution={execution} />
    </Box>
  );
};
