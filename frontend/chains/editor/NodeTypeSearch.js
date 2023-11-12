import React, {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { getOptionStyle, NodeSelector } from "chains/editor/NodeSelector";
import { useDebounce } from "utils/hooks/useDebounce";
import {
  Badge,
  Box,
  HStack,
  Input,
  InputGroup,
  InputRightElement,
  Spinner,
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
import { SelectedNodeContext } from "chains/editor/contexts";
import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { ComponentTypeMultiSelect } from "chains/editor/ComponentTypeMultiSelect";

const NodeSelectorHeader = ({ label, icon }) => {
  const { color, isLight } = useSideBarColorMode();
  const style = getOptionStyle(isLight);

  return (
    <HStack
      sx={{ userSelect: "none" }}
      width="100%"
      color={color}
      borderBottom="1px solid"
      borderColor="gray.600"
      px={2}
      pt={1}
      {...style.label}
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
    <Box mx={2} px={2} width={"100%"}>
      <NodeSelectorHeader label={typeKey} icon={typeStyle.icon} />
      {group?.map((type) => {
        return <NodeSelector key={type.id} type={type} />;
      })}
    </Box>
  );
};

const NodeTypeSearchBadge = ({ type, onRemove }) => {
  const { highlight } = useEditorColorMode();
  const onRemoveClick = useCallback(() => {
    onRemove(type);
  }, [type]);
  return (
    <Badge key={type} px={2} mr={1} bg={highlight[type]}>
      <Text
        as={"span"}
        color={"blackAlpha.500"}
        style={{ cursor: "pointer" }}
        onClick={onRemoveClick}
      >
        <FontAwesomeIcon icon={faXmark} size={"sm"} />
      </Text>{" "}
      {type}
    </Badge>
  );
};

/**
 * Provides a search widget including a search bar and a list of components.
 * Searching queries SearchNodeTypeQuery
 */
export const NodeTypeSearch = ({ initialFocusRef }) => {
  const { border } = useSideBarColorMode();
  const { input: inputStyle, scrollbar } = useEditorColorMode();
  const { selectedConnector } = useContext(SelectedNodeContext);
  const [query, setQuery] = useState({ search: "", types: [] });

  // component query
  const { load, page, clearPage, isLoading } = usePaginatedAPI(
    `/api/node_types/`,
    {
      load: false,
      limit: 50,
    }
  );
  const { callback: debouncedLoad, clear: clearLoad } = useDebounce(load, 400);

  // trigger query when query state changes
  useEffect(() => {
    if (query.search || query.types.length > 0) {
      if (selectedConnector && query.search === "") {
        // load immediately if there is a selected connector
        // since it indicates the user is not typing
        load(query);
      } else {
        // typing should always be debounced even
        // if there is a selected connector
        debouncedLoad(query);
      }
    } else {
      clearLoad();
      clearPage();
    }
  }, [query]);

  // auto-trigger state change when connector is [de]selected
  useEffect(() => {
    if (selectedConnector) {
      const { connector } = selectedConnector;
      const types = Array.isArray(connector.source_type)
        ? connector.source_type
        : [connector?.source_type];
      setQuery((prev) => ({ search: "", types }));
    } else {
      // clear query
      setQuery((prev) => ({ search: "", types: [] }));
    }
  }, [selectedConnector]);

  // callback for search bar changing
  const onSearchChange = useCallback((event) => {
    setQuery((prev) => ({ ...prev, search: event.target.value }));
  }, []);

  const handleTypeChange = useCallback(
    (types) => {
      setQuery((prev) => ({ ...prev, types }));
    },
    [setQuery]
  );

  const groupedTypes = useMemo(() => {
    return groupByNodeTypeGroup(page?.objects || []);
  }, [page]);

  return (
    <Box
      mt={2}
      pt={0}
      width="100%"
      minWidth={170}
      overflowY={"hidden"}
      maxHeight={"calc(100vh - 170px)"}
    >
      <Box px={3} pb={1}>
        <ComponentTypeMultiSelect
          value={query.types}
          onChange={handleTypeChange}
        />
      </Box>
      <Box px={2}>
        <InputGroup>
          <Input
            onChange={onSearchChange}
            placeholder="search components"
            mt={2}
            mb={2}
            mx={1}
            borderColor={border}
            value={query.search}
            {...inputStyle}
            ref={initialFocusRef}
          />
          <InputRightElement>
            {isLoading && <Spinner size={"sm"} />}
          </InputRightElement>
        </InputGroup>
      </Box>
      <VStack
        overflowY="auto"
        css={scrollbar}
        maxHeight={"calc(100vh - 170px)"}
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
