import React from "react";
import {
  Box,
  Button,
  HStack,
  Text,
  FormControl,
  FormLabel,
  FormHelperText,
  FormErrorMessage,
  useToast,
} from "@chakra-ui/react";

import { useCreateUpdateAPI } from "utils/hooks/useCreateUpdateAPI";
import { ModalClose } from "components/Modal";
import { SkillDeleteButton } from "skills/SkillDeleteButton";
import { NameField } from "chains/editor/fields/NameField";
import CodeEditor from "components/code_editor/CodeEditor";
import { RequiredAsterisk } from "components/RequiredAsterisk";

// Example python class with typehints and description. docstring should
const CODE_PLACEHOLDER =
  "def run(a: int) -> int:\n" +
  '    """Describe your skill here."""\n' +
  "    return a + 1";

const CODE_HELP = "Typed python function that implements this skill.";

export const SkillForm = ({ skill, onSuccess }) => {
  const toast = useToast();
  const [isEdit, setIsEdit] = React.useState(skill?.id !== undefined);
  const [data, setData] = React.useState(
    // initialize without func_name, description, and schema fields
    // so that they are updated from code only
    skill
      ? {
          id: skill.id,
          name: skill.name,
          code: skill.code,
        }
      : {
          name: "",
        }
  );

  const [valid, setValid] = React.useState(true);
  const onClose = React.useContext(ModalClose);

  const { save, error } = useCreateUpdateAPI(
    "/api/skills/",
    `/api/skills/${skill?.id}`
  );

  const onSave = React.useCallback(() => {
    save({ ...data }).then((response) => {
      toast({
        title: "Skill saved",
        description: `${data.name} saved`,
        status: "success",
        duration: 2000,
        isClosable: true,
        position: "bottom-right",
      });

      onSuccess(response);
      onClose();
    });
  }, [data, save]);

  // Callback for changing a set of fields in data
  const onDataChange = (updates) => {
    setData((data) => ({ ...data, ...updates }));
  };

  const handleCodeChange = (code) => {
    setData((data) => ({ ...data, code }));
  };

  return (
    <Box>
      <NameField onChange={onDataChange} value={data.name} mb={4} />
      <FormControl name="code" isInvalid={error !== undefined}>
        <FormLabel justify="start">
          Function <RequiredAsterisk />
        </FormLabel>
        <CodeEditor
          value={data.code}
          language="python"
          onChange={handleCodeChange}
          placeholder={CODE_PLACEHOLDER}
        />
        {!error && <FormHelperText>{CODE_HELP}</FormHelperText>}
        <FormErrorMessage>
          {error?.data?.detail?.map((err_datum) => (
            <Text>{err_datum.msg}</Text>
          ))}
        </FormErrorMessage>
      </FormControl>
      <HStack display="flex" justifyContent="flex-end" mt={4} mr={7}>
        {skill?.id && <SkillDeleteButton skill={skill} onSuccess={onSuccess} />}
        <Button colorScheme="blue" onClick={onSave} isDisabled={!valid}>
          Save
        </Button>
        <Button onClick={onClose}>Close</Button>
      </HStack>
    </Box>
  );
};
