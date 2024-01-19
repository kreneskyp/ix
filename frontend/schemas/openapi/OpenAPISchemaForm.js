import React from "react";
import {
  FormControl,
  FormErrorMessage,
  FormLabel,
  HStack,
  IconButton,
  Input,
  InputGroup,
  InputRightElement,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useDebounce } from "utils/hooks/useDebounce";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRefresh, faCheck, faX } from "@fortawesome/free-solid-svg-icons";
import { StyledIcon } from "components/StyledIcon";
import { NameField } from "chains/editor/fields/NameField";
import { DescriptionField } from "chains/editor/fields/DescriptionField";

const InputSpinner = () => {
  return <Spinner size="sm" />;
};

export const OpenAPISchemaForm = ({ schema, onChange, ...props }) => {
  const [state, setState] = React.useState(null);
  const style = useEditorColorMode();

  const fetchSchema = React.useCallback(async (url) => {
    setState({ icon: { component: InputSpinner } });
    try {
      const response = await fetch(url);
      if (!response.ok) {
        setState({ color: "red.300", icon: faX, error: response.statusText });
        return;
      }

      const data = await response.json();
      onChange({
        name: data.info?.title,
        description: data.info?.description,
        value: data,
      });
      setState({ color: "green.300", icon: faCheck });
    } catch (e) {
      setState({ color: "red.300", icon: faX });
    }
  }, []);

  const debouncedFetch = useDebounce(fetchSchema, 500);

  const handleChange = React.useCallback((new_url) => {
    onChange({ meta: { url: new_url } });
    if (new_url) {
      setState(null);
      return debouncedFetch.callback(new_url);
    }
    return () => debouncedFetch.clear();
  }, []);

  return (
    <VStack spacing={4} align="stretch" width={"100%"} {...props}>
      <FormControl id="url" isInvalid={state?.error !== undefined}>
        <FormLabel>URL</FormLabel>
        <HStack>
          <InputGroup>
            <Input
              placeholder="Enter OpenAPI schema URL"
              value={schema?.meta?.url}
              onChange={(e) => handleChange(e.target.value)}
              {...style.input}
            />
            <InputRightElement>
              {state && (
                <Text color={state.color}>
                  <StyledIcon style={state.icon} />
                </Text>
              )}
            </InputRightElement>
          </InputGroup>
          <IconButton
            icon={<FontAwesomeIcon icon={faRefresh} />}
            onClick={() => fetchSchema(url)}
          />
        </HStack>
        <FormErrorMessage>{state?.error}</FormErrorMessage>
      </FormControl>

      <NameField
        onChange={onChange}
        object={schema}
        isDisabled={schema === undefined}
      />
      <DescriptionField
        onChange={onChange}
        isDisabled={schema === undefined}
        object={schema}
      />
    </VStack>
  );
};

export default OpenAPISchemaForm;
