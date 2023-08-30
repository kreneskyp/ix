import React, { useCallback, useContext, useEffect, useMemo } from "react";
import { NodeSelector } from "chains/editor/NodeSelector";
import { useDebounce } from "utils/hooks/useDebounce";
import {
  Badge,
  Box,
  Heading,
  HStack,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react";
import {
  useEditorColorMode,
  useSideBarColorMode,
} from "chains/editor/useColorMode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { DEFAULT_NODE_STYLE, NODE_STYLES } from "chains/editor/styles";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { SelectedNodeContext } from "chains/editor/SelectedNodeContext";
import { faXmark } from "@fortawesome/free-solid-svg-icons";

const NodeSelectorHeader = ({ label, icon }) => {
  const { color } = useSideBarColorMode();

  return (
    <HStack
      sx={{ userSelect: "none" }}
      width="100%"
      color={color}
      borderBottom="1px solid"
      borderColor="gray.600"
      px={2}
      pt={1}
    >
      <FontAwesomeIcon icon={icon} />
      <Text>{label}</Text>
    </HStack>
  );
};

const SCROLLBAR_CSS = {
  "&::-webkit-scrollbar": {
    width: "5px",
  },
  "&::-webkit-scrollbar-track": {
    background: "transparent",
  },
  "&::-webkit-scrollbar-thumb": {
    background: "#333",
    borderRadius: "4px",
  },
  "&::-webkit-scrollbar-thumb:hover": {
    background: "#555",
  },
};

// Some components are grouped together in search results
// to simplify how many groups there are.
const NODE_TYPE_GROUP_OPTIONS = [
  {
    key: "memory",
    types: new Set(["memory", "memory_backend"]),
  },
];

// group by NodeType.type
const groupByNodeTypeType = (nodeTypes) => {
  const groups = {};
  for (const nodeType of nodeTypes) {
    if (!groups[nodeType.type]) {
      groups[nodeType.type] = [];
    }
    groups[nodeType.type].push(nodeType);
  }
  return groups;
};

// Group NodeType groups that are related
const groupByNodeTypeGroup = (nodeTypes) => {
  const groups = groupByNodeTypeType(nodeTypes);
  const groupList = {};
  for (const [groupKey, group] of Object.entries(groups)) {
    // look for group options, default key to the type name
    // if no group options are defined.
    const options = NODE_TYPE_GROUP_OPTIONS.find((groupOptions) =>
      groupOptions.types.has(groupKey)
    );
    const key = options?.key || groupKey;

    // add nodeTypes to the unified lists
    if (!groupList[key]) {
      groupList[key] = [...group];
    } else {
      groupList[key] = groupList[key].concat(group);
    }
  }

  // convert to sorted list
  return Object.entries(groupList).sort((a, b) => {
    return a[0].localeCompare(b[0]);
  });
};

const NodeTypeGroup = ({ typeKey, group }) => {
  const typeStyle = NODE_STYLES[typeKey] || DEFAULT_NODE_STYLE;

  return (
    <Box width="95%">
      <NodeSelectorHeader label={typeKey} icon={typeStyle.icon} />
      {group?.map((type) => {
        return <NodeSelector key={type.id} type={type} />;
      })}
    </Box>
  );
};

/**
 * Provides a search widget including a search bar and a list of components.
 * Searching queries SearchNodeTypeQuery
 */
export const NodeTypeSearch = () => {
  const { border } = useSideBarColorMode();

  // queries
  const { load, page } = usePaginatedAPI(`/api/node_types/`, { load: false });
  const { callback: searchNodeTypes, clear } = useDebounce(
    useCallback((search) => {
      load({ search });
    }, []),
    500
  );

  // callback for search bar changing
  const onSearchChange = useCallback((event) => {
    const search = event.target.value;
    if (search) {
      searchNodeTypes(search);
    } else {
      clear();
    }
  }, []);

  const groupedTypes = useMemo(() => {
    return groupByNodeTypeGroup(page?.objects || []);
  }, [page]);

  return (
    <Box
      mt={5}
      pt={5}
      width="100%"
      maxHeight={"60vh"}
      minWidth={170}
      overflowY={"hidden"}
    >
      <Heading as="h3" size="xs" mb={2}>
        Components
      </Heading>
      <Input
        onChange={onSearchChange}
        placeholder="search components"
        mb={2}
        borderColor={border}
      />
      <VStack
        overflowY="scroll"
        css={SCROLLBAR_CSS}
        maxHeight={"60vh"}
        spacing={2}
        width="100%"
      >
        {groupedTypes?.map(([key, group]) => {
          return <NodeTypeGroup key={key} typeKey={key} group={group} />;
        })}
      </VStack>
    </Box>
  );
};
