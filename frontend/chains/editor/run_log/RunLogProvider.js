import React from "react";
import { RunLog } from "chains/editor/contexts";
import { useAxios } from "utils/hooks/useAxios";
import { useDisclosure } from "@chakra-ui/react";
import { useRunEventStream } from "chains/editor/run_log/useRunEventStream";

export const RunLogProvider = ({ chain_id, children }) => {
  const disclosure = useDisclosure();
  const { call, response, error } = useAxios();

  const [log, setLog] = React.useState(null);
  const [execution, setExecution] = React.useState(null);

  const getLog = React.useCallback(() => {
    if (chain_id !== undefined) {
      call(`/api/runs/${chain_id}/latest/log`)
        .then((resp) => {})
        .catch((err) => {});
    }
  }, [chain_id]);

  React.useEffect(() => {
    if (chain_id !== undefined) {
      getLog();
    }
  }, [chain_id]);

  const onRunStart = React.useCallback((event) => {
    setLog({
      task_id: event.task_id,
      executions: [],
    });
  }, []);

  const onExecutionUpdate = React.useCallback((event) => {
    setLog((prev) => {
      const isNew =
        prev.executions.find((e) => e.id === event.id) === undefined;
      let executions;
      if (isNew) {
        executions = [...prev.executions, event];
      } else {
        executions = prev.executions.map((e) => {
          return e.id === event.id ? event : e;
        });
      }
      return { ...prev, executions };
    });
  }, []);

  useRunEventStream(chain_id, { onRunStart, onExecutionUpdate });

  React.useEffect(() => {
    if (response?.data) {
      setLog(response.data);
    }
  }, [response]);

  const log_by_node = React.useMemo(() => {
    const log_by_node = {};
    if (log) {
      log.executions?.forEach((event) => {
        log_by_node[event.node_id] = event;
      });
    }
    return log_by_node;
  }, [log]);

  const state = React.useMemo(() => {
    const has_errors = log?.executions?.some((e) => e.completed === false);
    const has_unknown = log?.executions?.some((e) => e.completed === null);
    const inProgress = log?.executions?.some((e) => e.finished_at === null);
    const has_executions = log?.executions?.length > 0;
    const completed =
      has_executions && !inProgress && !has_errors && !has_unknown;
    return {
      has_errors,
      has_unknown,
      completed,
      inProgress,
    };
  }, [log]);

  const value = React.useMemo(() => {
    return {
      log,
      state,
      log_by_node,
      execution,
      setExecution,
      getLog,
      disclosure,
    };
  }, [log, state, log_by_node, execution, setExecution, getLog, disclosure]);

  return <RunLog.Provider value={value}>{children}</RunLog.Provider>;
};
