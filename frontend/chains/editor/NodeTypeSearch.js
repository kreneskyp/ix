import { usePreloadedQuery, useQueryLoader } from "react-relay/hooks";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { NodeSelector } from "chains/editor/NodeSelector";
import { useDebounce } from "utils/hooks/useDebounce";
import { Box, Heading, HStack, Input, Text, VStack } from "@chakra-ui/react";
import { SearchNodeTypesQuery } from "chains/graphql/SearchNodeTypesQuery";
import { DEFAULT_NODE_STYLE, NODE_STYLES } from "chains/flow/ConfigNode";
import { useSideBarColorMode } from "chains/editor/useColorMode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

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

const SearchNodeTypesQueryRunner = ({ queryRef, setResults }) => {
  // load query and then update state
  const data = usePreloadedQuery(SearchNodeTypesQuery, queryRef);
  const nodeTypes = data?.searchNodeTypes;
  useEffect(() => {
    setResults(nodeTypes);
  }, [queryRef, nodeTypes]);
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
  const [results, setResults] = useState([]);
  const { border } = useSideBarColorMode();

  // queries
  const [nodeTypesQueryRef, loadNodeTypesQuery, disposeNodeTypesQuery] =
    useQueryLoader(SearchNodeTypesQuery);
  const { callback: searchNodeTypes, clear } = useDebounce(
    useCallback((search) => {
      loadNodeTypesQuery({ search }, { fetchPolicy: "store-and-network" });
    }, []),
    500
  );

  const onSearchChange = useCallback((event) => {
    const search = event.target.value;
    if (search) {
      searchNodeTypes(search);
    } else {
      clear();
      if (nodeTypesQueryRef) {
        disposeNodeTypesQuery();
      }
      if (results) {
        setResults([]);
      }
    }
  }, []);

  // Couldn't determine a good pattern for using relay to fetch
  // search updates for the autocomplete. The results are needed
  // here to decide whether to render the popover or not.
  //
  // QueryRunner components render empty but will fetch the query
  // data then update the results state. This is a huge hack but
  // it works for now.
  const nodeTypeSearchRunner = nodeTypesQueryRef !== null && (
    <SearchNodeTypesQueryRunner
      queryRef={nodeTypesQueryRef}
      setResults={setResults}
    />
  );

  const groupedTypes = useMemo(() => {
    return groupByNodeTypeGroup(results || []);
  }, [results]);

  return (
    <Box
      mt={5}
      pt={5}
      width="100%"
      maxHeight={"60vh"}
      minWidth={170}
      overflowY={"hidden"}
    >
      {nodeTypeSearchRunner}
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
