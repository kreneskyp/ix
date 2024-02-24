from ix.api.components.types import NodeTypeField, NodeType, Connector


LOAD_SKILL_CLASS_PATH = "ix.skills.runnable.LoadSkill"
LOAD_SKILL = NodeType(
    class_path=LOAD_SKILL_CLASS_PATH,
    name="Load Skill",
    description="Get a skill from the IX skill registry",
    type="chain",
    connectors=[
        Connector(
            key="out",
            label="Skill",
            type="source",
            source_type="flow",
        )
    ],
    fields=[
        NodeTypeField(
            name="skill_id",
            label="Skill",
            type="string",
            description="Skill to load",
            input_type="IX:skill",
        ),
    ],
)


RUN_SKILL_CLASS_PATH = "ix.skills.runnable.RunSkill.from_db"
RUN_SKILL = NodeType(
    class_path=RUN_SKILL_CLASS_PATH,
    name="Run Skill",
    description="Run a skill",
    type="chain",
    fields=[
        NodeTypeField(
            name="skill_id",
            label="Skill",
            type="string",
            description="Skill to run",
            input_type="IX:skill",
        ),
        NodeTypeField(
            name="raise_error",
            label="Halt on error",
            type="boolean",
            description="Halt on error by raising exception",
            default=False,
        ),
    ],
)

SKILLS = [LOAD_SKILL, RUN_SKILL]
