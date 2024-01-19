import React from "react";
import { Select, components } from "chakra-react-select";
import { Box, Text, FormHelperText, VStack } from "@chakra-ui/react";

import { getOptionStyle } from "chains/editor/ComponentTypeSelect";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { useSelectStyles } from "components/select/useSelectStyles";
import { MenuList } from "components/select/MenuList";
import { useOpenAPISchema } from "schemas/openapi/useOpenAPISchema";
import { useChakraStyles } from "components/select/useChakraStyles";

const SELECT_SCHEMA_TEXT = "First select a schema";
const SELECT_SERVER_TEXT = "Select server for request";

const ServerOption = ({ server, ...props }) => {
  if (!server) {
    return null;
  }

  return (
    <VStack spacing={0} py={1} px={2} alignItems={"start"} {...props}>
      <Text fontSize={"xs"} m={0}>
        {server.description}
      </Text>
      <FormHelperText fontSize={"xs"} m={0}>
        {server.url}
      </FormHelperText>
    </VStack>
  );
};

const ValueContainer = ({ children, ...props }) => {
  const { getValue } = props;
  const value = getValue()[0];
  const server = value?.value;

  return (
    <components.ValueContainer {...props} p={0} m={0}>
      <ServerOption server={server} />
    </components.ValueContainer>
  );
};

const useOpenAPIServerOptions = (schema) => {
  return React.useMemo(() => {
    return schema?.servers?.map((server) => {
      return {
        value: server,
        label: server.description,
        helpText: server.url,
      };
    });
  }, [schema]);
};

export const SchemaServerSelect = ({ config, onChange, value }) => {
  const chakraStyles = useChakraStyles();
  const schema = useOpenAPISchema(config?.schema_id)[0];
  const options = useOpenAPIServerOptions(schema?.value);

  const valueOption = React.useMemo(() => {
    return options?.find((option) => option.value.url === value);
  }, [options, value]);

  const handleChange = (newValue) => {
    onChange(newValue.value.url);
  };

  const CustomOption = React.useMemo(() => {
    return ({ data, selectOption }) => {
      const { isLight, highlight } = useEditorColorMode();
      const style = getOptionStyle(isLight);
      return (
        <ServerOption
          server={data.value}
          mx={1}
          cursor={"pointer"}
          _hover={style.hover}
          onClick={() => selectOption(data)}
        />
      );
    };
  }, [value, onChange]);

  return (
    <Box>
      <Select
        options={options}
        value={valueOption}
        styles={useSelectStyles()}
        menuPortalTarget={document.body}
        chakraStyles={chakraStyles}
        components={{ Option: CustomOption, MenuList, ValueContainer }}
        onChange={handleChange}
      />
      <FormHelperText fontSize={"xs"}>
        {schema?.value === undefined
          ? SELECT_SCHEMA_TEXT
          : valueOption?.value
          ? null
          : SELECT_SERVER_TEXT}
      </FormHelperText>
    </Box>
  );
};
