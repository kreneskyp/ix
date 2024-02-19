import React from "react";

import { Box, HStack } from "@chakra-ui/react";
import { ExecutionList } from "chains/editor/run_log/ExecutionList";
import { useRunLog } from "chains/editor/run_log/useRunLog";
import { ExecutionDetail } from "chains/editor/run_log/ExecutionDetail";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const RunLog = ({}) => {
  const { log, execution, setExecution, extra_nodes, extra_types } =
    useRunLog();
  const { scrollbar } = useEditorColorMode();

  return (
    <HStack alignItems="start">
      <Box
        overflowY={"auto"}
        height={"calc(100vh - 250px)"}
        css={scrollbar}
        pl={2}
        minWidth={"260px"}
      >
        <ExecutionList
          log={log}
          extra_nodes={extra_nodes}
          extra_types={extra_types}
          selectedExecution={execution}
          setExecution={setExecution}
        />
      </Box>
      <Box
        width="100%"
        overflowY={"auto"}
        height={"calc(100vh - 250px)"}
        css={scrollbar}
      >
        <ExecutionDetail execution={execution?.execution} />
      </Box>
    </HStack>
  );
};
