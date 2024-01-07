import React from "react";
import {
  Badge,
  Box,
  HStack,
  List,
  ListItem,
  Text,
  VStack,
} from "@chakra-ui/react";
import { ExecutionStatusIcon } from "chains/editor/run_log/icons";
import { ChainTypes, NodeStateContext } from "chains/editor/contexts";
import { useEditorColorMode } from "chains/editor/useColorMode";

const ExecutionBrief = ({ nodes, types, execution, onClick }) => {
  const node = nodes?.[execution.node_id];
  const type = types?.find((t) => t.id === node?.node_type_id);
  const { badge, highlight } = useEditorColorMode();
  return (
    <HStack cursor={"pointer"} onClick={onClick}>
      <Box px={2}>
        <ExecutionStatusIcon execution={execution} />
      </Box>
      <Box fontSize={"xs"}>
        <Badge
          bg={highlight[type?.type] || highlight.default}
          size={"xs"}
          mx={1}
          my={2}
          {...badge}
        >
          {type?.type || "unknown"}
        </Badge>
        <Text>{type?.name || node.class_path.split(".").pop()}</Text>
      </Box>
    </HStack>
  );
};

export const ExecutionList = ({ log, selectedExecution, setExecution }) => {
  const { nodes } = React.useContext(NodeStateContext);
  const executions =
    log?.executions.filter((e) => nodes?.[e.node_id] !== undefined) || [];
  const [types, setTypes] = React.useContext(ChainTypes);

  const { isLight } = useEditorColorMode();
  const itemStyle = isLight
    ? {
        borderColor: "gray.200",
        _hover: { bg: "blackAlpha.200" },
      }
    : {
        borderColor: "gray.600",
        _hover: { bg: "blackAlpha.400" },
      };
  const selectedItemStyle = isLight
    ? {
        bg: "blackAlpha.200",
      }
    : {
        bg: "blackAlpha.400",
      };

  return (
    <Box>
      <VStack alignItems={"start"}>
        <List alignItems={"start"} px={2}>
          {executions.map((execution, i) => {
            return (
              <ListItem
                key={i}
                p={2}
                borderBottom={
                  i !== executions.length - 1 ? "1px solid" : "none"
                }
                {...itemStyle}
                {...(selectedExecution?.id === execution.id
                  ? selectedItemStyle
                  : {})}
              >
                <ExecutionBrief
                  nodes={nodes}
                  types={types}
                  execution={execution}
                  onClick={() => setExecution(execution)}
                />
              </ListItem>
            );
          })}
        </List>
      </VStack>
    </Box>
  );
};
