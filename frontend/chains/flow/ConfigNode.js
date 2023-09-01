import React, { useCallback, useContext, useMemo } from "react";
import { Box, Flex, Heading, VStack } from "@chakra-ui/react";
import { Handle, useEdges, useReactFlow } from "reactflow";
import { faTrash } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import { DEFAULT_NODE_STYLE, NODE_STYLES } from "chains/editor/styles";
import { RequiredAsterisk } from "components/RequiredAsterisk";
import { ConnectorPopover } from "chains/editor/ConnectorPopover";
import { NodeStateContext, SelectedNodeContext } from "chains/editor/contexts";

const CONNECTOR_CONFIG = {
  agent: {
    source_position: "left",
    target_position: "right",
  },
  chain: {
    source_position: "left",
    target_position: "right",
  },
  tool: {
    source_position: "left",
    target_position: "right",
  },
  toolkit: {
    source_position: "left",
    target_position: "right",
  },
};

const usePropertyTargets = (node, type) => {
  const edges = useEdges();

  return useMemo(() => {
    const connectors = type.connectors?.filter(
      (connector) => connector.type === "target"
    );
    return connectors?.map((connector) => {
      const edge = edges?.find(
        (edge) => edge.target === node.id && edge.targetHandle === connector.key
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
  const source_type = Array.isArray(connector.source_type)
    ? connector.source_type[0]
    : connector.source_type;

  const position = CONNECTOR_CONFIG[source_type]?.target_position || "left";

  return (
    <Box position="relative" width="100%">
      <Handle id={connector.key} type="target" position={position} />
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
    const source_type = Array.isArray(connector.source_type)
      ? connector.source_type[0]
      : connector.source_type;
    const position = CONNECTOR_CONFIG[source_type]?.target_position || "left";
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
  const styles = NODE_STYLES[type.type] || DEFAULT_NODE_STYLE;
  const { border, color, highlight, highlightColor, bg, selectionShadow } =
    useEditorColorMode();
  const position = CONNECTOR_CONFIG[type.type]?.source_position || "right";
  const { nodes } = useContext(NodeStateContext);
  const node = nodes[data.node.id];

  const nodeStyle = {
    color,
    border: "1px solid",
    borderColor: border,
    backgroundColor: bg,
    boxShadow: selected ? selectionShadow : "md",
  };

  if (!node) {
    return null;
  }

  // node type specific content
  let NodeComponent = null;
  if (styles?.component) {
    NodeComponent = styles.component;
  }
  const node_component_props = {
    type,
    node,
  };
  const content = NodeComponent ? (
    <NodeComponent {...node_component_props} />
  ) : (
    <DefaultNodeContent {...node_component_props} />
  );

  return (
    <Box p={5} className="config-node">
      <Box
        borderWidth="0px"
        borderRadius={8}
        padding="0"
        minWidth={250}
        {...nodeStyle}
      >
        <Handle
          id={type.type}
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
          bg={highlight[type.type] || highlight.default}
          px={1}
          py={2}
          className="drag-handle"
        >
          <Flex alignItems="center" justifyContent="space-between" width="100%">
            <Box pr={5}>
              <FontAwesomeIcon icon={styles?.icon} />{" "}
              {node.name || type?.name || node.class_path.split(".").pop()}
            </Box>
            <DeleteIcon node={node} />
          </Flex>
        </Heading>
        <Box minHeight={25} cursor="default">
          {content}
        </Box>
      </Box>
    </Box>
  );
};

export default ConfigNode;
