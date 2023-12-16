import React from "react";
import { Select } from "chakra-react-select";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleQuestion } from "@fortawesome/free-solid-svg-icons";
import { Box, HStack, Text } from "@chakra-ui/react";

import { useEditorColorMode } from "chains/editor/useColorMode";
import { NODE_STYLES } from "chains/editor/styles";
import {
  COMPONENT_TYPE_OPTIONS,
  MenuList,
  useSelectStyles,
} from "chains/editor/ComponentTypeSelect";
import { getOptionStyle } from "chains/editor/NodeSelector";

export const ComponentTypeMultiSelect = ({ onChange, value, ...props }) => {
  const { input: styles, highlight } = useEditorColorMode();
  const chakraStyles = {
    control: (base) => ({ ...base, ...styles, width: "100%" }),
    dropdownIndicator: (base) => ({ ...base, ...styles, px: 2 }),
    multiValue: (base, { data }) => ({
      ...base,
      ...styles,
      color: "white",
      bg: highlight[data.value],
      ml: 1,
      mr: 0,
      px: 1,
      borderRadius: 2,
    }),
    multiValueLabel: (base) => ({ ...base, color: "white", mx: 0, px: 0 }),
    multiValueRemove: (base) => ({ ...base, color: "white", mx: 0, px: 0 }),
  };

  const selectStyles = useSelectStyles();

  const CustomOption = React.useMemo(() => {
    return ({ data, selectOption, ...props }) => {
      const { isLight, highlight } = useEditorColorMode();
      const style = getOptionStyle(isLight);

      return (
        <HStack
          my={3}
          mx={2}
          pr={1}
          cursor={"pointer"}
          onClick={() => {
            selectOption(data);
          }}
          _hover={style.hover}
          borderLeft={"6px solid"}
          borderLeftColor={highlight[data.value]}
          borderRadius={5}
        >
          <Box>
            <Text p={3} {...style.icon}>
              <FontAwesomeIcon
                icon={NODE_STYLES[data.value]?.icon || faCircleQuestion}
              />
            </Text>
          </Box>
          <Box>
            <Text fontWeight="bold" {...style.label}>
              {data.label}
            </Text>
            <Text fontSize="xs" {...style.help}>
              {data.helpText}
            </Text>
          </Box>
        </HStack>
      );
    };
  }, [onChange]);

  const handleChange = (newValue, action) => {
    // handle actions: select-option, remove-value, pop-value, set-value, clear
    if (action.action === "select-option") {
      onChange([...value, newValue[newValue.length - 1].value]);
    } else if (action.action === "remove-value") {
      onChange(value.filter((v) => v !== action.removedValue.value));
    } else if (action.action === "clear") {
      onChange([]);
    } else if (action.action === "set-value") {
      onChange(newValue.map((v) => v.value));
    } else if (action.action === "pop-value") {
      onChange(value.slice(0, -1));
    }
  };

  const valueOptions = React.useMemo(() => {
    // convert to array of value/label objects
    return value.map((v) => ({ value: v, label: v }));
  }, [value]);

  return (
    <Box {...props} px={0} m={0}>
      <Select
        isMulti
        placeholder={"select component types"}
        onChange={handleChange}
        options={COMPONENT_TYPE_OPTIONS}
        value={valueOptions}
        styles={selectStyles}
        menuPortalTarget={document.body}
        chakraStyles={chakraStyles}
        components={{ Option: CustomOption, MenuList }}
        className="basic-multi-select"
        classNamePrefix="select"
      />
    </Box>
  );
};
