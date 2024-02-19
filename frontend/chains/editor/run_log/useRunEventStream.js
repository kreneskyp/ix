import React from "react";
import { RunEventSubscription } from "chains/editor/run_log/RunEventSubscription";
import { requestSubscription } from "react-relay";
import environment from "relay-environment";

export const useRunEventStream = (
  chain_id,
  { onRunStart, onExecutionUpdate } = {}
) => {
  const [connectionActive, setConnectionActive] = React.useState(false);
  let subscription;

  React.useEffect(() => {
    if (chain_id === undefined || chain_id === null) {
      return;
    }

    const connect = () => {
      setConnectionActive(true);
      subscription = requestSubscription(environment, {
        subscription: RunEventSubscription,
        variables: { chainId: chain_id },
        updater: (store, data) => {
          const payload = store.getRootField("runEventSubscription");
          const event = payload.getLinkedRecord("event");

          if (event) {
            const eventType = event.getType();
            const eventData = data.runEventSubscription.event;
            if (eventType === "ExecutionType" && onExecutionUpdate) {
              const formatted = {
                id: eventData.id,
                parent_id: eventData.parentId,
                node_id: eventData.nodeId,
                started_at: eventData.startedAt,
                finished_at: eventData.finishedAt,
                completed: eventData.completed,
                inputs: eventData.inputs,
                outputs: eventData.outputs,
                message: eventData.message,
              };
              onExecutionUpdate(formatted);
            } else if (eventType === "RunStartType" && onRunStart) {
              onRunStart({ task_id: eventData.taskId });
            }
          }
        },
        onError: (error) => {
          console.error("An error occurred:", error);
          setConnectionActive(false);

          // Reconnect after a delay
          setTimeout(connect, 5000);
        },
      });
    };

    connect();

    return () => {
      if (subscription) {
        subscription.dispose();
      }
      setConnectionActive(false);
    };
  }, [chain_id]);

  return connectionActive;
};
