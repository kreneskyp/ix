import React, {
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";
import { Box, Flex, Heading, VStack } from "@chakra-ui/react";
import { Handle, useEdges, useReactFlow } from "reactflow";
import { faTrash } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { PromptNode } from "chains/flow/PromptNode";
import { ChainEditorAPIContext } from "chains/editor/ChainEditorAPIContext";
import { TypeAutoFields } from "chains/flow/TypeAutoFields";
import { CollapsibleSection } from "chains/flow/CollapsibleSection";
import { useDebounce } from "utils/hooks/useDebounce";
import { FunctionSchemaNode } from "chains/flow/FunctionSchemaNode";
import { DEFAULT_NODE_STYLE, NODE_STYLES } from "chains/editor/styles";
import { RequiredAsterisk } from "components/RequiredAsterisk";

const NODE_COMPONENTS = {
  "langchain.prompts.chat.ChatPromptTemplate": PromptNode,
  "ix.chains.functions.FunctionSchema": FunctionSchemaNode,
};

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

export const useConnectorColor = (connector) => {
  const { connector: connectorStyle } = useEditorColorMode();
  if (connector.connected) {
    return connectorStyle.connected;
  } else if (connector.required) {
    return connectorStyle.required;
  } else {
    return connectorStyle.default;
  }
};

export const PropertyTarget = ({ connector }) => {
  const color = useConnectorColor(connector);

  return (
    <Box position="relative" width="100%">
      <Handle
        id={connector.key}
        type="target"
        position={
          CONNECTOR_CONFIG[connector.source_type]?.target_position || "left"
        }
      />
      <Box px={2} m={0} color={color}>
        {connector.key}{" "}
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
    const position =
      CONNECTOR_CONFIG[connector.source_type]?.target_position || "left";
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
          <PropertyTarget key={index} connector={connector} />
        ))}
      </VStack>
      <VStack spacing={0} cursor="default">
        {right?.map((connector, index) => (
          <PropertyTarget key={index} connector={connector} />
        ))}
      </VStack>
    </Flex>
  );
};

export const DefaultNodeContent = ({ type, config, node, onFieldChange }) => {
  return (
    <>
      <NodeProperties node={node} type={type} />
      <CollapsibleSection title="Config">
        <TypeAutoFields type={type} config={config} onChange={onFieldChange} />
      </CollapsibleSection>
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

export const ConfigNode = ({ data }) => {
  const { type, node } = data;
  const styles = NODE_STYLES[type.type] || DEFAULT_NODE_STYLE;
  const { border, color, highlight, highlightColor, bg } = useEditorColorMode();
  const [config, setConfig] = useState(node.config);

  const api = useContext(ChainEditorAPIContext);

  // ref for handlers to access latest config without re-rendering
  const configRef = useRef();
  configRef.current = config;

  const { callback: debouncedUpdateNode } = useDebounce(api.updateNode, 1000);
  const handleConfigChange = useMemo(() => {
    function all(newConfig, delay = 0) {
      const data = {
        class_path: node.class_path,
        description: node.description,
        position: node.position,
        config: newConfig,
      };
      debouncedUpdateNode(node.id, data);
      setConfig(newConfig);
    }

    const field = (key, value, delay = 1000) => {
      const newConfig = { ...configRef.current, [key]: value };
      all(newConfig, delay);
    };

    return { all, field };
  }, [node.id, api, configRef]);

  // node type specific content
  let NodeComponent = null;
  if (NODE_COMPONENTS[node.class_path]) {
    NodeComponent = NODE_COMPONENTS[node.class_path];
  } else if (styles?.component) {
    NodeComponent = styles.component;
  }
  const node_component_props = {
    type,
    node,
    config,
    onChange: handleConfigChange.all,
    onFieldChange: handleConfigChange.field,
  };
  const content = NodeComponent ? (
    <NodeComponent {...node_component_props} />
  ) : (
    <DefaultNodeContent {...node_component_props} />
  );
  const position = CONNECTOR_CONFIG[type.type]?.source_position || "right";

  return (
    <Box p={5} className="config-node">
      <Box
        borderWidth="0px"
        borderRadius={8}
        padding="0"
        border="1px solid"
        borderColor={border}
        backgroundColor={bg}
        minWidth={styles?.width || 250}
        color={color}
        boxShadow="md"
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
