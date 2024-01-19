import React from "react";
import { Select, components } from "chakra-react-select";
import { Box, HStack, Text } from "@chakra-ui/react";
import { getOptionStyle } from "chains/editor/ComponentTypeSelect";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { faCircleQuestion } from "@fortawesome/free-solid-svg-icons";
import { StyledIcon } from "components/StyledIcon";
import { JSONSchemaIcon } from "icons/JSONSchemaIcon";
import { OpenAPIIcon } from "icons/OpenAPIIcon";
import { useSelectStyles } from "components/select/useSelectStyles";
import { MenuList } from "components/select/MenuList";

const JSON_HELP_TEXT = "Schema for data generation, extraction, and validation";
const OPENAPI_HELP_TEXT = "Schema for API access";

export const SCHEMA_TYPE_OPTIONS = [
  {
    value: "json",
    label: "JSON",
    helpText: JSON_HELP_TEXT,
    icon: { component: JSONSchemaIcon },
  },
  {
    value: "openapi",
    label: "OpenAPI",
    helpText: OPENAPI_HELP_TEXT,
    icon: { component: OpenAPIIcon },
  },
];

const ValueContainer = ({ children, ...props }) => {
  const { getValue } = props;
  const value = getValue()[0];
  const { isLight } = useEditorColorMode();
  const iconColor = isLight ? "gray.100" : "gray.100";

  const schema_option = SCHEMA_TYPE_OPTIONS.find(
    (option) => option.value === value.value
  );

  return (
    <components.ValueContainer {...props}>
      <HStack p={0} m={0}>
        {value ? (
          <Box
            pl={2}
            m={0}
            height={"38px"}
            display="flex"
            alignItems="center"
            justifyContent="center"
            color={iconColor}
          >
            <StyledIcon
              style={schema_option?.icon || { icon: faCircleQuestion }}
            />
          </Box>
        ) : null}
        {children}
      </HStack>
    </components.ValueContainer>
  );
};

export const SchemaTypeSelect = ({ onChange, value, ...props }) => {
  const { input: styles } = useEditorColorMode();
  const chakraStyles = {
    control: (base) => ({ ...base, ...styles, width: 400 }),
    dropdownIndicator: (base) => ({ ...base, ...styles }),
  };

  const valueOption = React.useMemo(() => {
    return { value: value, label: value };
  }, [value]);

  const CustomOption = React.useMemo(() => {
    const onClick = (newValue) => {
      onChange({ type: newValue.value });
    };

    return ({ data }) => {
      const { isLight } = useEditorColorMode();
      const style = getOptionStyle(isLight);

      return (
        <HStack
          my={3}
          cursor={"pointer"}
          _hover={style.hover}
          onClick={() => onClick(data)}
        >
          <Box p={3} {...style.icon}>
            <StyledIcon style={data.icon} />
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
  }, [value, onChange]);

  return (
    <Box {...props}>
      <Select
        default={"json"}
        options={SCHEMA_TYPE_OPTIONS}
        value={valueOption}
        styles={useSelectStyles()}
        menuPortalTarget={document.body}
        chakraStyles={chakraStyles}
        components={{ Option: CustomOption, MenuList, ValueContainer }}
      />
    </Box>
  );
};
