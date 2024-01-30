import React from "react";
import { SkillForm } from "skills/SkillForm";
import { ModalTrigger, ModalTriggerContent } from "components/Modal";
import { Box } from "@chakra-ui/react";

export const SkillFormModalButton = ({
  skill,
  onOpen,
  onSuccess,
  children,
  type,
}) => {
  return (
    <ModalTrigger
      onOpen={onOpen}
      showClose={false}
      size="6xl"
      title={"Edit Skill"}
      closeOnBlur={false}
    >
      {children}
      <ModalTriggerContent>
        <Box p={4}>
          <SkillForm skill={skill} type={type} onSuccess={onSuccess} />
        </Box>
      </ModalTriggerContent>
    </ModalTrigger>
  );
};

export default SkillFormModalButton;
