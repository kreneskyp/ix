import React, {
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";
import { Box, Flex, Heading, VStack } from "@chakra-ui/react";
import { Handle, useReactFlow } from "reactflow";
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

const NODE_COMPONENTS = {
  "langchain.prompts.chat.ChatPromptTemplate": PromptNode,
  "ix.chains.functions.FunctionSchema": FunctionSchemaNode,
};

const usePropertyTargets = (type) => {
  return useMemo(() => {
    return type.connectors?.filter((connector) => connector.type === "target");
  }, [type]);
};

export const PropertyTarget = ({ connector }) => {
  return (
    <Box position="relative" width="100%">
      <Handle
        id={connector.key}
        type="target"
        position={connector.sourceType === "chain" ? "right" : "left"}
      />
      <Box pl={2} m={0}>
        {connector.key}
      </Box>
    </Box>
  );
};

export const NodeProperties = ({ type }) => {
  const propertyTargets = usePropertyTargets(type);
  return (
    <VStack spacing={0} cursor="default">
      {propertyTargets?.map((connector, index) => (
        <PropertyTarget key={index} connector={connector} />
      ))}
    </VStack>
  );
};

export const DefaultNodeContent = ({ type, config, onFieldChange }) => {
  return (
    <>
      <NodeProperties type={type} />
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
      api.deleteNode({ id: node.id });
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
        id: node.id,
        classPath: node.classPath,
        description: node.description,
        position: node.position,
        config: newConfig,
      };
      debouncedUpdateNode({ data });
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
  if (NODE_COMPONENTS[node.classPath]) {
    NodeComponent = NODE_COMPONENTS[node.classPath];
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

  return (
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
        position={type.type === "chain" ? "left" : "right"}
        style={{ top: "15px", transform: "translateX(-2px)" }}
      />
      <Heading
        as="h4"
        size="xs"
        color={highlightColor}
        borderTopLeftRadius={7}
        borderTopRightRadius={7}
        bg={highlight[type.type]}
        px={1}
        py={2}
        className="drag-handle"
      >
        <Flex alignItems="center" justifyContent="space-between" width="100%">
          <Box>
            <FontAwesomeIcon icon={styles?.icon} />{" "}
            {node.name || node.classPath.split(".").pop()}
          </Box>
          <DeleteIcon node={node} />
        </Flex>
      </Heading>
      <Box minHeight={25} cursor="default">
        {content}
      </Box>
    </Box>
  );
};

export default ConfigNode;
