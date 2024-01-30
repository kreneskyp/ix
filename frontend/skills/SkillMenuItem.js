import React from "react";
import { Box, Button, Flex, Text, Spinner } from "@chakra-ui/react";
import { usePaginatedAPI } from "utils/hooks/usePaginatedAPI";

import {
  LeftMenuPopover,
  LeftSidebarPopupContent,
  LeftSidebarPopupHeader,
  LeftSidebarPopupIcon,
} from "site/LeftMenuPopover";
import { SkillTable } from "skills/SkillTable";
import { SkillFormModalButton } from "skills/SkillFormModalButton";
import { MenuItem } from "site/MenuItem";
import { SkillIcon } from "skills/SkillIcon";
import { useEditorColorMode } from "chains/editor/useColorMode";

export const SkillMenuItem = ({ editor }) => {
  const style = useEditorColorMode();
  const { page, isLoading, load } = usePaginatedAPI("/api/skills/", {
    loadDependencies: [location],
    limit: 90000,
    load: false,
  });

  return (
    <LeftMenuPopover onOpen={load}>
      <LeftSidebarPopupIcon>
        <MenuItem title="Skills">
          <SkillIcon {...style.menu_icon} />
        </MenuItem>
      </LeftSidebarPopupIcon>
      <LeftSidebarPopupHeader>
        <Flex width={"100%"} justifyContent={"space-between"}>
          <Text>Skills</Text>
          <SkillFormModalButton onSuccess={load} type={"json"}>
            <Button colorScheme="green" size={"xs"}>
              Add Skill
            </Button>
          </SkillFormModalButton>
        </Flex>
        <Text {...style.help}>
          JSON Skills defining data types for data extraction & generation.
        </Text>
      </LeftSidebarPopupHeader>
      <LeftSidebarPopupContent width={800}>
        {isLoading ? (
          <Box
            height={"200px"}
            width={500}
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            <Spinner size="xl" />
          </Box>
        ) : (
          <Box width={500}>
            <SkillTable page={page} load={load} type={"json"} />
          </Box>
        )}
      </LeftSidebarPopupContent>
    </LeftMenuPopover>
  );
};

SkillMenuItem.defaultProps = {
  editor: false,
};
