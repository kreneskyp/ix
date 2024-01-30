import React from "react";
import { DraggableNode } from "chains/editor/DraggableNode";
import { ListItemNode } from "components/ListItemNode";

const DRAGGABLE_CONFIG = {
  class_path: "ix.skills.runnable.RunSkill.from_db",
  label: "Run Skill",
};

export const SkillDraggable = ({ skill }) => {
  return (
    <DraggableNode
      {...DRAGGABLE_CONFIG}
      name={skill.func_name}
      description={skill.description}
      config={{ skill_id: skill.id }}
      height={"100%"}
    >
      <ListItemNode label={"Run Skill"} />
    </DraggableNode>
  );
};
