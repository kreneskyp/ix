import React from "react";
import { DeleteButton } from "components/DeleteButton";

export const SkillDeleteButton = ({ skill, onSuccess }) => {
  const deleteUrl = `/api/skills/${skill?.id}`;
  const confirmationMessage = `Are you sure you want to delete the skill '${skill?.name}'? This action cannot be undone.`;

  return (
    <DeleteButton
      item={skill}
      onSuccess={onSuccess}
      deleteUrl={deleteUrl}
      confirmationMessage={confirmationMessage}
      itemName="Skill"
    />
  );
};
