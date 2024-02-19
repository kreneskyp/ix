import React from "react";
import {
  Badge,
  Box,
  HStack,
  IconButton,
  Text,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faChevronDown,
  faChevronRight,
} from "@fortawesome/free-solid-svg-icons";
import { ExecutionStatusIcon } from "chains/editor/run_log/icons";
import { ChainTypes, NodeStateContext } from "chains/editor/contexts";
import { useEditorColorMode } from "chains/editor/useColorMode";
import TreeItem, { BranchLine } from "chains/editor/run_log/Tree";
import { StyledIcon } from "components/StyledIcon";
import { DEFAULT_NODE_STYLE, NODE_STYLES } from "chains/editor/styles";
import { useRunLog } from "chains/editor/run_log/useRunLog";

const useExecutionTree = (executions, nodes, types) => {
  const buildTree = (items, parentId = null) => {
    return (
      items
        ?.filter((item) => item.parent_id === parentId)
        ?.map((item) => {
          const node = nodes?.[item.node_id];
          return {
            execution: item,
            children: buildTree(items, item.id),
            node: node,
            type: types?.find((t) => t.id === node?.node_type_id),
          };
        }) || []
    );
  };

  return React.useMemo(() => {
    return buildTree(executions);
  }, [executions, nodes, types]);
};

const ExecutionIcon = ({ type, isLight }) => {
  const styles = NODE_STYLES[type?.type] || DEFAULT_NODE_STYLE;
  const iconStyle = isLight
    ? {
        color: "gray.600",
      }
    : {
        color: "gray.200",
      };
  return (
    <Text {...iconStyle}>
      <StyledIcon style={styles.icon} {...iconStyle} />
    </Text>
  );
};

const ExecutionBrief = ({ execution, node, type }) => {
  const { badge, highlight } = useEditorColorMode();
  return (
    <Box pl={2}>
      <HStack>
        <Badge
          bg={highlight[type?.type] || highlight.default}
          fontSize={10}
          mx={0}
          my={1}
          {...badge}
        >
          {type?.type || "unknown"}
        </Badge>
        <Text fontSize={10}>
          <ExecutionStatusIcon execution={execution.execution} />{" "}
        </Text>
      </HStack>
      <Text fontSize={12} width={120} overflowX={"hidden"}>
        {type?.name || node?.class_path.split(".").pop() || "unknown"}
      </Text>
    </Box>
  );
};

const ExecutionTreeNode = ({ execution, isFirst, isLast }) => {
  const { execution: selectedExecution, setExecution } = useRunLog();

  const onClick = () => {
    setExecution(execution);
  };
  const isSelected = selectedExecution?.execution.id === execution.execution.id;
  const { isOpen, onToggle } = useDisclosure();

  const { isLight } = useEditorColorMode();
  const itemStyle = isLight
    ? {
        borderColor: "gray.200",
        _hover: { bg: "blackAlpha.200" },
      }
    : {
        borderColor: "gray.600",
        _hover: { bg: "blackAlpha.400", borderRadius: 3 },
      };
  const selectedItemStyle = isLight
    ? {
        bg: "blackAlpha.200",
      }
    : {
        bg: "blackAlpha.400",
      };

  const children = execution.children.map((child, i) => (
    <ExecutionTreeNode
      key={i}
      execution={child}
      isFirst={i === 0}
      isLast={i === execution.children.length - 1}
    />
  ));

  return (
    <Box p={0} height={"100%"}>
      <HStack
        cursor={"pointer"}
        onClick={onClick}
        height={"60px"}
        py={0}
        px={2}
        whiteSpace={"nowrap"}
        {...(isSelected ? selectedItemStyle : itemStyle)}
        width={"100%"}
      >
        <TreeItem isFirst={isFirst} isLast={isLast}>
          <ExecutionIcon type={execution.type} isLight={isLight} />
        </TreeItem>
        <ExecutionBrief
          execution={execution}
          node={execution.node}
          type={execution.type}
        />
        <Box height={"100%"} alignItems={"end"} display={"flex"} width={"35px"}>
          {execution.children.length > 0 && (
            <IconButton
              fontSize={10}
              h={5}
              px={0}
              variant="ghost"
              onClick={onToggle}
              icon={
                <FontAwesomeIcon
                  icon={isOpen ? faChevronDown : faChevronRight}
                />
              }
            />
          )}
        </Box>
      </HStack>

      {isOpen && (
        <HStack bg={"transparent"} height={"100%"} spacing={0}>
          <BranchLine height={execution.children.length * 60} />
          {children.length > 1 && <VStack spacing={0}>{children}</VStack>}
        </HStack>
      )}
    </Box>
  );
};

export const ExecutionList = ({ log }) => {
  const { nodes } = React.useContext(NodeStateContext);
  const [types, setTypes] = React.useContext(ChainTypes);

  const executions = useExecutionTree(log?.executions, nodes, types);

  return (
    <Box width={"200px"}>
      <VStack alignItems={"start"} spacing={0}>
        {executions.map((execution, i) => (
          <ExecutionTreeNode
            key={execution.execution.id}
            execution={execution}
            isFirst={i === 0}
            isLast={i === executions.length - 1}
          />
        ))}
      </VStack>
    </Box>
  );
};
