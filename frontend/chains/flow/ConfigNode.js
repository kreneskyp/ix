import React, { useCallback, useContext, useMemo } from "react";
import { Box, Flex, Heading, HStack, Text, VStack } from "@chakra-ui/react";
import { Handle, useEdges, useReactFlow } from "reactflow";
import { faTrash } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import { DEFAULT_NODE_STYLE, NODE_STYLES } from "chains/editor/styles";
import { RequiredAsterisk } from "components/RequiredAsterisk";
import { ConnectorPopover } from "chains/editor/ConnectorPopover";
import {
  NodeStateContext,
  RunLog,
  SelectedNodeContext,
} from "chains/editor/contexts";
import { StyledIcon } from "components/StyledIcon";
import { NodeExecutionIcon } from "chains/editor/run_log/NodeExecutionIcon";

const CONNECTOR_CONFIG = {
  agent: {
    source_position: "right",
    target_position: "left",
  },
  chain: {
    source_position: "right",
    target_position: "left",
  },
  tool: {
    source_position: "right",
    target_position: "left",
  },
  toolkit: {
    source_position: "right",
    target_position: "left",
  },
};

const usePropertyTargets = (node, type) => {
  const edges = useEdges();

  return useMemo(() => {
    const connectors = type?.connectors || [];
    return connectors?.map((connector) => {
      const edge = edges?.find(
        (edge) =>
          (edge.target === node.id && edge.targetHandle === connector.key) ||
          (edge.source === node.id && edge.sourceHandle === connector.key)
      );
      return { ...connector, connected: !!edge };
    });
  }, [type, edges, node.id]);
};

export const useConnectorColor = (node, connector) => {
  const { selectedConnector } = useContext(SelectedNodeContext);
  const { connector: connectorStyle } = useEditorColorMode();
  if (
    connector.key === selectedConnector?.connector.key &&
    node.id === selectedConnector?.node.id
  ) {
    return connectorStyle.selected;
  } else if (connector.connected) {
    return connectorStyle.connected;
  } else if (connector.required) {
    return connectorStyle.required;
  } else {
    return connectorStyle.default;
  }
};

export const PropertyTarget = ({ type, node, connector }) => {
  const color = useConnectorColor(node, connector);
  const position = connector.type === "source" ? "right" : "left";

  return (
    <Box position="relative" width="100%">
      <Handle id={connector.key} type={connector.type} position={position} />
      <Box px={2} m={0} color={color}>
        <ConnectorPopover
          type={type}
          node={node}
          connector={connector}
          placement={position}
        />{" "}
        {connector.required && <RequiredAsterisk color={color} />}
      </Box>
    </Box>
  );
};

export const NodeProperties = ({ node, type }) => {
  const propertyTargets = usePropertyTargets(node, type);

  // sort properties into left and right
  const left = [];
  const right = [];
  propertyTargets?.forEach((connector) => {
    if (connector.key === "in" || connector.key === "out") {
      return;
    }

    const position = connector.type === "source" ? "right" : "left";
    if (position === "right") {
      right.push(connector);
    } else {
      left.push(connector);
    }
  });

  return (
    <Flex justify={"space-between"}>
      <VStack spacing={0} cursor="default">
        {left?.map((connector, index) => (
          <PropertyTarget
            key={index}
            type={type}
            node={node}
            connector={connector}
          />
        ))}
      </VStack>
      <VStack spacing={0} cursor="default">
        {right?.map((connector, index) => (
          <PropertyTarget
            key={index}
            type={type}
            node={node}
            connector={connector}
          />
        ))}
      </VStack>
    </Flex>
  );
};

export const DefaultNodeContent = ({ type, node }) => {
  return (
    <>
      <NodeProperties node={node} type={type} />
    </>
  );
};

const DeleteIcon = ({ node }) => {
  const api = useContext(ChainEditorAPIContext);
  const { setNodes, setEdges } = useReactFlow();

  const onClick = useCallback(
    (event) => {
      api.deleteNode(node.id);
    },
    [node.id, api]
  );

  return (
    <Box mr={3} cursor="pointer" onClick={onClick}>
      <FontAwesomeIcon icon={faTrash} />
    </Box>
  );
};

export const ConfigNode = ({ id, data, selected }) => {
  const { type } = data;
  const styles = NODE_STYLES[type?.type] || DEFAULT_NODE_STYLE;
  const { border, color, highlight, highlightColor, bg, selectionShadow } =
    useEditorColorMode();
  const position = CONNECTOR_CONFIG[type?.type]?.source_position || "right";
  const nodeState = useContext(NodeStateContext);
  const { nodes } = nodeState;
  const node = nodes[data.node.id];

  // run log when available
  const { log_by_node } = React.useContext(RunLog);
  const run_event = log_by_node[node?.id];

  const nodeStyle = {
    color,
    border: "1px solid",
    borderColor: border,
    backgroundColor: bg,
    boxShadow: selected ? selectionShadow : "md",
  };

  // node type specific content
  const content = React.useMemo(() => {
    let NodeComponent = null;
    if (styles?.component) {
      NodeComponent = styles.component;
    }
    const node_component_props = {
      type,
      node,
    };
    return NodeComponent ? (
      <NodeComponent {...node_component_props} />
    ) : (
      <DefaultNodeContent {...node_component_props} />
    );
  }, [type, node, styles]);

  if (!node) {
    return null;
  }

  return (
    <Box p={5} className="config-node">
      <Box
        borderWidth="0px"
        borderRadius={8}
        padding="0"
        minWidth={200}
        {...nodeStyle}
      >
        <Handle
          id={type?.type}
          type="source"
          position={position}
          style={{
            top: "38px",
            transform:
              position === "left" ? "translateX(23px)" : "translateX(-23px)",
          }}
        />
        <Heading
          as="h4"
          size="xs"
          color={highlightColor}
          borderTopLeftRadius={7}
          borderTopRightRadius={7}
          bg={highlight[type?.type] || highlight.default}
          px={1}
          py={2}
          className="drag-handle"
        >
          <Flex alignItems="center" justifyContent="space-between" width="100%">
            <HStack pr={5} h={"16px"}>
              <StyledIcon style={styles?.icon} />{" "}
              <Text>
                {node.name || type?.name || node.class_path.split(".").pop()}
              </Text>
            </HStack>
            <DeleteIcon node={node} />
          </Flex>
        </Heading>
        <Box position={"absolute"} top={5} right={0}>
          <NodeExecutionIcon node={node} />
        </Box>
        <Box minHeight={25} cursor="default">
          {content}
        </Box>
      </Box>
    </Box>
  );
};

export default ConfigNode;
