import React from "react";
import { RunLog } from "chains/editor/contexts";
import { useAxios } from "utils/hooks/useAxios";

export const RunLogProvider = ({ chain_id, children }) => {
  const { call, response, error } = useAxios();

  React.useEffect(() => {
    if (false && chain_id !== undefined) {
      call(`/api/runs/${chain_id}/latest/log`)
        .then((resp) => {})
        .catch((err) => {});
    }
  }, [chain_id]);

  const log_by_node = React.useMemo(() => {
    const log_by_node = {};
    if (response?.data) {
      response.data.executions.forEach((event) => {
        log_by_node[event.node_id] = event;
      });
    }
    return log_by_node;
  }, [response]);

  const value = {
    refresh: call,
    log: response?.data || [],
    log_by_node,
  };

  return <RunLog.Provider value={value}>{children}</RunLog.Provider>;
};
