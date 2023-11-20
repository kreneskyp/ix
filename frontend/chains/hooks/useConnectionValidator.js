import { useMemo } from "react";
import { useReactFlow } from "reactflow";

export const useConnectionValidator = (edgeUpdate) => {
  const reactFlowInstance = useReactFlow();

  const isValidConnection = useMemo(() => {
    return ({
      source,
      target,
      sourceHandle,
      targetHandle,
      sourceType,
      targetType,
    }) => {
      // TODO: disabling all validation until rules can be updated for flow changes
      return true;

      // target
      // hax: targetNode isn't available when creating a new node
      //      require targetType when not available
      const targetNode = reactFlowInstance.getNode(target);
      const targetNodeType = targetType || targetNode.data.type;
      const connectors = targetNodeType.connectors;
      let connector, expectedTypes;
      if (targetHandle === "in") {
        expectedTypes = new Set(["chain-link"]);
      } else {
        connector = connectors.find((c) => c.key === targetHandle);
        expectedTypes = Array.isArray(connector?.source_type)
          ? new Set(connector.source_type)
          : new Set([connector.source_type]);
      }
      const supportsMultiple = connector?.multiple || false;

      // source
      // hax: sourceNode isn't available when creating a new node
      //      require sourceType when not available
      const sourceNode = reactFlowInstance.getNode(source);
      const providedType =
        sourceHandle === "out"
          ? "chain-link"
          : (sourceType || sourceNode.data.type).type;

      // Check connection types
      if (
        expectedTypes.has(providedType) ||
        (expectedTypes.has("chain") && providedType === "agent")
      ) {
        const instanceEdges = reactFlowInstance.getEdges();
        const targetEdges = instanceEdges.filter(
          (e) => e.target === target && e.targetHandle === targetHandle
        );
        const sourceEdges = instanceEdges.filter(
          (e) => e.source === source && e.sourceHandle === sourceHandle
        );

        const sourceConnected = sourceEdges.length > 0;
        const targetConnected = targetEdges.length > 0;

        if (edgeUpdate.edge) {
          const currentSource = edgeUpdate.edge.source;
          const currentTarget = edgeUpdate.edge.target;
          const isSameSource = source === currentSource;
          const isSameTarget = target === currentTarget;

          return (
            (isSameSource || !sourceConnected) &&
            (isSameTarget || !targetConnected || supportsMultiple)
          );
        } else {
          return !sourceConnected && (!targetConnected || supportsMultiple);
        }
      }

      return false;
    };
  }, [reactFlowInstance, edgeUpdate]);

  return {
    isValidConnection,
  };
};
