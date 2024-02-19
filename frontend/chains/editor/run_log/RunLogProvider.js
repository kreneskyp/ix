import React from "react";
import { ChainTypes, NodeStateContext, RunLog } from "chains/editor/contexts";
import { useAxios } from "utils/hooks/useAxios";
import { useDisclosure } from "@chakra-ui/react";
import { useRunEventStream } from "chains/editor/run_log/useRunEventStream";
import { addNodes, addTypes } from "chains/utils";

export const RunLogProvider = ({ chain_id, children }) => {
  const disclosure = useDisclosure();
  const { call, response, error } = useAxios();
  const { call: fetch_nodes } = useAxios({ method: "post" });

  const [types, setTypes] = React.useContext(ChainTypes);
  const { nodes, setNodes } = React.useContext(NodeStateContext);

  const [log, setLog] = React.useState(null);
  const [execution, setExecution] = React.useState(null);

  const getLog = React.useCallback(() => {
    if (chain_id !== undefined) {
      call(`/api/runs/${chain_id}/latest/log`)
        .then((resp) => {})
        .catch((err) => {});
    }
  }, [chain_id]);

  // preemptively load any nodes that are missing from local state
  // this loads nodes & types for any executions for nested chains
  React.useEffect(() => {
    if (log) {
      const missing_nodes = log.executions
        ?.map((e) => e.node_id)
        ?.filter((id) => !nodes[id]);

      if (missing_nodes?.length > 0) {
        fetch_nodes(`/api/nodes/bulk`, {
          data: missing_nodes,
        })
          .then((resp) => {
            addTypes(resp.data.types, setTypes);
            addNodes(resp.data.nodes, setNodes);
          })
          .catch((err) => {
            console.error("Failed to load missing nodes", err);
          });
      }
    }
  }, [log]);

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
  }, [log, nodes, types]);

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

  // HAX: force refresh of log object whenever types or nodes changes.
  //      this is a cheap way of injecting this dependency into the log object
  //      so downstream components don't need to know that nodes or types have
  //      changed.
  const _log = React.useMemo(() => ({ ...log }), [log, types, nodes]);

  const value = React.useMemo(() => {
    return {
      log: _log,
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
