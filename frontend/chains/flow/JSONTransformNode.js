import React from "react";
import {
  Box,
  FormControl,
  FormHelperText,
  FormLabel,
  Input,
  InputGroup,
  InputRightElement,
  Link,
  Text,
  Tooltip,
  Select,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faList, faExternalLink } from "@fortawesome/free-solid-svg-icons";
import ListForm from "components/ListForm";
import DictForm from "components/DictForm";
import { useEditorColorMode } from "chains/editor/useColorMode";

const DEFAULT_PATH = { path: "", is_list: false };

const PathInput = ({ value, onChange }) => {
  const style = useEditorColorMode();
  const isList = value?.is_list === true;

  const handleIconClick = () => {
    onChange({
      target: { value: { ...(value || DEFAULT_PATH), is_list: !isList } },
    });
  };

  const handlePathChange = (e) => {
    onChange({
      target: { value: { ...(value || DEFAULT_PATH), path: e.target.value } },
    });
  };

  const iconStyle = {
    cursor: "pointer",
    color: isList ? "blue.400" : style.isLight ? "gray.400" : "gray.600",
  };

  return (
    <InputGroup>
      <Input
        value={value?.path}
        onChange={handlePathChange}
        placeholder={"$.json.path.to.value"}
        {...style.input}
      />
      <InputRightElement>
        <Tooltip label={`${isList ? "Always" : "Single value or "} List`}>
          <Box onClick={handleIconClick} {...iconStyle}>
            <FontAwesomeIcon icon={faList} />
          </Box>
        </Tooltip>
      </InputRightElement>
    </InputGroup>
  );
};

const SinglePathForm = ({ data, onChange }) => {
  return (
    <>
      <FormLabel>Single Value</FormLabel>
      <PathInput value={data} onChange={(e) => onChange(e.target.value)} />
    </>
  );
};

const ListPathForm = ({ data, onChange }) => {
  return (
    <ListForm
      label="List of paths"
      list={Array.isArray(data) ? data : []}
      component={PathInput}
      defaultValue={DEFAULT_PATH}
      onChange={onChange}
    />
  );
};

const ObjectPathForm = ({ data, onChange }) => {
  return (
    <DictForm
      label="Object of paths"
      dict={data || {}}
      component={PathInput}
      onChange={onChange}
    />
  );
};

const JSONPathLink = () => {
  return (
    <Link mx={2} href="https://goessner.net/articles/JsonPath/" isExternal>
      <Text
        as={"span"}
        color={"blue.300"}
        css={{ textDecoration: "underline dotted" }}
        mr={1}
      >
        JSON Path
      </Text>
      <FontAwesomeIcon icon={faExternalLink} size={"xs"} />
    </Link>
  );
};

const BASE_SINGLE = 1;
const BASE_LIST = 2;
const BASE_OBJECT = 3;
const FORMS_MAP = {
  [BASE_SINGLE]: {
    Form: SinglePathForm,
    help: (
      <Text>
        {"Enter a single"}
        <JSONPathLink />
        {"expression to return."}
      </Text>
    ),
  },
  [BASE_LIST]: {
    Form: ListPathForm,
    help: (
      <Text>
        {"Enter a list of"}
        <JSONPathLink />
        {
          "expressions. A list will be returned containing the values at each path."
        }
      </Text>
    ),
  },
  [BASE_OBJECT]: {
    Form: ObjectPathForm,
    help: (
      <Text>
        {"Enter a map of keys and "}
        <JSONPathLink />
        {
          "expressions. An object will be returned containing the values at each path."
        }
      </Text>
    ),
  },
};

/**
 * Custom node editor for JSONTransform nodes used to transform
 * inputs and outputs.
 *
 * Provides a choice of base type:
 * - single path
 * - list of paths
 * - object of paths
 *
 * Each path is a JSON path expression and is_list flag indicating
 * whether the path is always a list of values. When the path matches
 * 1 or 0 values and is_list=True, a list will be returned.
 *
 */
export const JSONTransformNode = ({ node, onChange }) => {
  const { Form, help } = FORMS_MAP[node.config.base] || FORMS_MAP[BASE_SINGLE];
  const style = useEditorColorMode();

  const handleChange = React.useCallback(
    (newData) => {
      onChange.field("json_path", newData);
    },
    [onChange.field]
  );

  console.log("node: ", node);

  const handleBaseChange = (e) => {
    const newBase = parseInt(e.target.value);
    onChange.config({
      ...node.config,
      base: newBase,
      json_path: {
        [BASE_SINGLE]: DEFAULT_PATH,
        [BASE_LIST]: [],
        [BASE_OBJECT]: {},
      }[newBase],
    });
  };

  return (
    <Box mt={5}>
      <FormControl label="Type" mb={5}>
        <FormLabel justify="start" whiteSpace="nowrap" mr={0} pr={0}>
          Type
        </FormLabel>
        <Select
          value={node.config.base}
          placeholder={"Select object type"}
          onChange={handleBaseChange}
          width={"100%"}
          {...style.input}
        >
          <option value={BASE_SINGLE}>Single</option>
          <option value={BASE_LIST}>List</option>
          <option value={BASE_OBJECT}>Object</option>
        </Select>
        <FormHelperText fontSize={"xs"}>
          Root type of output: single value, list, or object.
        </FormHelperText>
      </FormControl>
      <FormControl label={"json_paths"}>
        <Form data={node.config?.json_path} onChange={handleChange} />
        <FormHelperText fontSize={"xs"}>{help}</FormHelperText>
      </FormControl>
    </Box>
  );
};
