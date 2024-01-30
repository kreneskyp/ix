import React from "react";
import { Box, HStack, Select, Tooltip } from "@chakra-ui/react";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlusCircle } from "@fortawesome/free-solid-svg-icons";
import { ModalTriggerButton } from "components/Modal";
import SkillFormModalButton from "skills/SkillFormModalButton";

export const SkillSelect = ({ value, onChange }) => {
  const style = useEditorColorMode();
  const { page, load, isLoading } = usePaginatedAPI("/api/skills/", {
    limit: 1000,
    load: false,
  });

  React.useEffect(() => {
    load().catch((err) => {
      console.error("failed to load skills", err);
    });
  }, []);

  // New Skill callback: refresh skills and select the new skill
  const loadAndSelect = (response) => {
    load().then(() => {
      onChange(response.id);
    });
  };

  const handleChange = (e) => {
    onChange(e.target.value);
  };

  return (
    <HStack>
      <SkillFormModalButton onSuccess={loadAndSelect}>
        <ModalTriggerButton>
          <Tooltip label="Add Skill">
            <Box
              color={"gray.500"}
              _hover={{ color: "green.400", bg: "transparent" }}
              mx={0}
            >
              <FontAwesomeIcon icon={faPlusCircle} />
            </Box>
          </Tooltip>
        </ModalTriggerButton>
      </SkillFormModalButton>
      <Select
        value={value || ""}
        onChange={handleChange}
        placeholder={"Select a skill"}
        {...style.input}
        ml={0}
      >
        {page?.objects?.map((skill) => (
          <option key={skill.id} value={skill.id}>
            {skill.name}
          </option>
        ))}
      </Select>
    </HStack>
  );
};
