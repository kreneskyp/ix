import React from "react";
import { Box, HStack, Text, VStack } from "@chakra-ui/react";
import { ModalTrigger } from "components/Modal";
import { SkillFormModalButton } from "skills/SkillFormModalButton";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { getOptionStyle } from "chains/editor/NodeSelector";
import { SkillDraggable } from "skills/SkillDraggable";

export const SkillTable = ({ type, page, load }) => {
  const { isLight } = useEditorColorMode();
  const style = getOptionStyle(isLight);

  return (
    <VStack alignItems={"start"} pt={2} px={2}>
      {page?.objects.map((skill, index) => (
        <HStack
          key={index}
          _hover={style.hover}
          height={75}
          borderRadius={5}
          width={"100%"}
        >
          <Box width={"100%"}>
            <SkillFormModalButton skill={skill} type={type} onSuccess={load}>
              <ModalTrigger.Button>
                <HStack p={3}>
                  <Box>
                    <Text {...style.label}>{skill.name}</Text>
                    <Text {...style.help}>{skill.description}</Text>
                  </Box>
                </HStack>
              </ModalTrigger.Button>
            </SkillFormModalButton>
          </Box>
          <SkillDraggable skill={skill} />
        </HStack>
      ))}
    </VStack>
  );
};
