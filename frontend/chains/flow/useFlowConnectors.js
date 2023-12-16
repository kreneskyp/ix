import React from "react";
import { useEdges } from "reactflow";
import { Text } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faExclamationTriangle } from "@fortawesome/free-solid-svg-icons";

const RUNNABLES = ["agent", "chain", "flow"];

export const UndefinedLabel = () => {
  return (
    <Text>
      <FontAwesomeIcon icon={faExclamationTriangle} /> Undefined
    </Text>
  );
};

export const useFlowConnectors = (node) => {
  const edges = useEdges();
  return React.useMemo(() => {
    if (!node) return {};

    return {
      // default output
      default: {
        key: "default",
        type: "source",
        source_type: RUNNABLES,
        required: false,
        connected: edges?.find(
          (edge) => edge.source === node.id && edge.sourceHandle === "default"
        ),
      },

      // static input
      input: {
        key: "in",
        // TODO: calculate label? or just disable for singular named inputs?
        label: "Input",
        type: "target",
        source_type: RUNNABLES,
        required: true,
        connected: edges?.find(
          (edge) => edge.target === node.id && edge.targetHandle === "in"
        ),
      },

      // configured inputs
      inputs: node?.config?.inputs_hash?.map((io_key, i) => ({
        key: io_key,
        label: node?.config?.inputs[i] || <UndefinedLabel />,
        type: "target",
        source_type: RUNNABLES,
        // TODO: need to calculate this
        required: false,
        connected: edges?.find(
          (edge) => edge.source === node.id && edge.sourceHandle === io_key
        ),
      })),

      // static output
      output: {
        key: "out",
        label: "Output",
        type: "source",
        source_type: RUNNABLES,
        required: false,
        connected: edges?.find(
          (edge) => edge.source === node.id && edge.sourceHandle === "out"
        ),
      },

      // configured outputs
      outputs: node?.config?.outputs_hash?.map((io_key, i) => ({
        key: io_key,
        label: node?.config?.outputs[i] || <UndefinedLabel />,
        type: "source",
        source_type: RUNNABLES,
        required: true,
        connected: edges?.find(
          (edge) => edge.source === node.id && edge.sourceHandle === io_key
        ),
      })),
    };
  }, [edges, node?.id, node?.config]);
};
