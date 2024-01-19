import React from "react";
import { Select, components } from "chakra-react-select";
import {
  Badge,
  Box,
  HStack,
  Text,
  FormHelperText,
  VStack,
  useDisclosure,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faClose } from "@fortawesome/free-solid-svg-icons";

import { getOptionStyle } from "chains/editor/ComponentTypeSelect";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { useOpenAPIActions } from "schemas/openapi/useOpenAPIActions";
import { METHOD_COLORS } from "schemas/openapi/SchemaPathsList";
import { JSONSchemaDisplay } from "schemas/json/JSONSchemaDisplay";
import { useSelectStyles } from "components/select/useSelectStyles";
import { MenuList } from "components/select/MenuList";
import { useInputSchema } from "schemas/openapi/useInputSchema";
import { useOpenAPISchema } from "schemas/openapi/useOpenAPISchema";
import { useChakraStyles } from "components/select/useChakraStyles";

const SELECT_SCHEMA_TEXT = "First select a schema";
const SELECT_ACTION_TEXT =
  "Select an API action to use for data generation, extraction, and validation";

const ActionOption = ({ method, path, operation, ...props }) => {
  if (!method) {
    return null;
  }

  return (
    <HStack p={0} m={0} {...props}>
      <Box pl={2} mx={1} w={10} display="flex" justifyContent="center">
        <Badge bg={METHOD_COLORS[method]} color={"white"}>
          {method}
        </Badge>
      </Box>
      <VStack spacing={0} py={1} alignItems={"start"}>
        <Text fontSize={"xs"} m={0}>
          {operation?.summary}
        </Text>
        <FormHelperText fontSize={"xs"} m={0}>
          {path}
        </FormHelperText>
      </VStack>
    </HStack>
  );
};

const ValueContainer = ({ children, ...props }) => {
  const { getValue } = props;
  const value = getValue()[0];

  return (
    <components.ValueContainer {...props}>
      <ActionOption {...(value?.value || {})} />
    </components.ValueContainer>
  );
};

const useOpenAPIActionOptions = (schema) => {
  const actions = useOpenAPIActions(schema) || [];
  return React.useMemo(() => {
    return actions.map((action) => {
      return {
        value: action,
        label: action.path,
        helpText: action.operation.summary,
        method: action.method,
      };
    });
  }, [actions]);
};

const ActionInstructionText = ({ schema }) => {
  const { isOpen, onToggle } = useDisclosure();

  return (
    <>
      <FormHelperText fontSize={"xs"}>
        Provide input according to the{" "}
        <Text
          cursor={"pointer"}
          color={"blue.400"}
          css={{ textDecoration: "underline dotted" }}
          onClick={onToggle}
          as={"span"}
        >
          JSON Schema
        </Text>
        .
      </FormHelperText>
      {isOpen && (
        <Box position={"relative"}>
          <Text
            cursor={"pointer"}
            onClick={onToggle}
            color={"gray.500"}
            _hover={{ color: "red.300" }}
            top={1}
            right={2}
            position={"absolute"}
            fontSize={"xs"}
          >
            Close <FontAwesomeIcon icon={faClose} />
          </Text>
          <JSONSchemaDisplay schema={schema} mt={1} />
        </Box>
      )}
    </>
  );
};

export const SchemaActionSelect = ({
  config,
  onConfigChange,
  value,
  ...props
}) => {
  const chakraStyles = useChakraStyles();
  const schema = useOpenAPISchema(config?.schema_id)[0];
  const options = useOpenAPIActionOptions(schema?.value);

  const valueOption = React.useMemo(() => {
    return options?.find(
      (option) =>
        option.value.path === config.path &&
        option.value.method === config.method
    );
  }, [options, config?.path, config?.method]);

  const inputSchema = useInputSchema(config?.schema_id, valueOption?.value)[0];

  const handleChange = (newValue) => {
    onConfigChange({
      path: newValue.value.path,
      method: newValue.value.method,
    });
  };

  const CustomOption = React.useMemo(() => {
    return ({ data, selectOption }) => {
      const { isLight } = useEditorColorMode();
      const style = getOptionStyle(isLight);
      return (
        <ActionOption
          {...data.value}
          cursor={"pointer"}
          _hover={style.hover}
          onClick={() => selectOption(data)}
        />
      );
    };
  }, [value, onConfigChange]);

  return (
    <Box {...props}>
      <Select
        options={options}
        value={valueOption}
        styles={useSelectStyles()}
        menuPortalTarget={document.body}
        chakraStyles={chakraStyles}
        onChange={handleChange}
        components={{ Option: CustomOption, MenuList, ValueContainer }}
      />
      <FormHelperText fontSize={"xs"}>
        {schema?.value === undefined
          ? SELECT_SCHEMA_TEXT
          : valueOption?.value
          ? null
          : SELECT_ACTION_TEXT}
      </FormHelperText>
      {inputSchema && <ActionInstructionText schema={inputSchema} />}
    </Box>
  );
};
