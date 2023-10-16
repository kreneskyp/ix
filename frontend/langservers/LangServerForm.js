import React from "react";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  FormHelperText,
  Input,
  Textarea,
  VStack,
  HStack,
  Tooltip,
  Spinner,
  InputGroup,
  InputRightElement,
  Text,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSyncAlt, faCheck, faX } from "@fortawesome/free-solid-svg-icons";

import { useCreateUpdateAPI } from "utils/hooks/useCreateUpdateAPI";
import { DictForm } from "components/DictForm";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { useDebounce } from "utils/hooks/useDebounce";
import { ModalClose } from "components/Modal";
import { LangServerDeleteButton } from "langservers/LangServerDeleteButton";

export const LangServerForm = ({ langserver, onSuccess }) => {
  const [data, setData] = React.useState(langserver || {});
  const [valid, setValid] = React.useState(data?.id ? data?.id : null);
  const [loading, setLoading] = React.useState(false);
  const onClose = React.useContext(ModalClose);
  const style = useEditorColorMode();

  const { save } = useCreateUpdateAPI(
    "/api/langservers/",
    `/api/langservers/${langserver?.id}`
  );

  const onSave = React.useCallback(() => {
    save(data).then(() => {
      onSuccess();
      onClose();
    });
  }, [data, save]);

  const onNameChange = React.useCallback(
    (e) => {
      setData((data) => ({ ...data, name: e.target.value }));
    },
    [data, setData]
  );

  // callback for importing langserve config from URL
  const setFromImport = React.useCallback(async (url) => {
    setLoading(true);
    setValid(null);
    const startTime = Date.now();
    const response = await fetch("/api/import_langserver/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });

    if (response.ok) {
      const langServerConfig = await response.json();
      setData((data) => ({ ...data, ...langServerConfig }));
      setValid(true);
    } else {
      setValid(false);
    }
    const endTime = Date.now();
    const diffTime = endTime - startTime;
    const minTime = 600
    if (diffTime < minTime) {
      setTimeout(() => setLoading(false), minTime - diffTime);
    } else {
      setLoading(false);
    }
  }, []);

  const { callback: debouncedFromImport } = useDebounce(setFromImport, 500);

  const onDescriptionChange = React.useCallback(
    (e) => {
      setData((data) => ({ ...data, description: e.target.value }));
    },
    [data, setData]
  );

  const onUrlChange = React.useCallback(
    async (e) => {
      const url = e.target.value;
      if (!url) {
        setValid(null);
        setData((data) => ({ ...data, url: "" }));
        return;
      }

      // Auto-import the first time the url is set
      const isValidURL = !!url.match(/^https?:\/\/[^\s/$.?#].[^\s]*$/);
      setData((data) => ({ ...data, url }));

      // reset import if url changes
      if (!isValidURL) {
        setValid(false);
      } else if (valid) {
        setValid(null);
      }

      if (isValidURL) {
        debouncedFromImport(url);
      }
    },
    [data, valid, setValid, setData, setFromImport]
  );

  const onHeaderChange = React.useCallback(
    (value) => {
      setData((data) => ({ ...data, headers: value || {} }));
    },
    [data, setData]
  );

  const onRefresh = React.useCallback(() => {
    setFromImport(data?.url);
  }, [data?.url]);

  // input displays status icon for importing from URL
  const validityIconProps = valid
    ? { icon: faCheck, color: "green" }
    : { icon: faX, color: "red" };
  const inputIcon = loading ? (
    <Spinner size="xs" />
  ) : valid !== null ? (
    <FontAwesomeIcon {...validityIconProps} />
  ) : null;

  const refreshStyle = style.isLight
    ? { enabled: "gray.800", disabled: "gray.400" }
    : { enabled: "gray.100", disabled: "gray.600" };

  return (
    <Box>
      <VStack spacing={5}>
        <FormControl>
          <FormLabel>URL</FormLabel>
          <HStack>
            <InputGroup>
              <Input
                value={data?.url || ""}
                onChange={onUrlChange}
                placeholder="Enter endpoint"
                {...style.input}
              />
              <InputRightElement children={inputIcon} />
            </InputGroup>
            <Tooltip label="Refresh from URL spec">
              <Text
                color={data?.url ? refreshStyle.enabled : refreshStyle.disabled}
              >
                <FontAwesomeIcon
                  icon={faSyncAlt}
                  onClick={data?.url ? onRefresh : null}
                  cursor="pointer"
                />
              </Text>
            </Tooltip>
          </HStack>
          <FormHelperText fontSize="xs">Enter URL to import</FormHelperText>
        </FormControl>

        <FormControl>
          <DictForm
            dict={data?.headers || {}}
            onChange={onHeaderChange}
            label="Headers"
            {...style.input}
          />
          <FormHelperText ml={5} fontSize="xs">
            Add headers to request, including authentication token if needed
          </FormHelperText>
        </FormControl>

        <FormControl>
          <FormLabel>Name</FormLabel>
          <Input
            value={data?.name || ""}
            onChange={onNameChange}
            placeholder="Enter name"
            {...style.input}
          />
        </FormControl>
        <FormControl>
          <FormLabel>Description</FormLabel>
          <Textarea
            value={data?.description || ""}
            onChange={onDescriptionChange}
            placeholder="Enter description"
            {...style.input}
          />
        </FormControl>
      </VStack>

      <HStack display="flex" justifyContent="flex-end" mt={4}>
        {langserver?.id && (
          <LangServerDeleteButton
            langserver={langserver}
            onSuccess={onSuccess}
          />
        )}
        <Button colorScheme="blue" onClick={onSave}>
          Save
        </Button>
        <Button onClick={onClose} variant="ghost">
          Close
        </Button>
      </HStack>
    </Box>
  );
};

export default LangServerForm;
