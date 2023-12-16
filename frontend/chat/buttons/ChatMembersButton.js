import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUsers } from "@fortawesome/free-solid-svg-icons";
import SideBarAgentList from "chat/sidebar/SideBarAgentList";
import { MenuItem } from "site/MenuItem";
import {
  LeftMenuPopover,
  LeftSidebarPopupContent,
  LeftSidebarPopupHeader,
  LeftSidebarPopupIcon,
} from "site/LeftMenuPopover";

export const ChatMembersButton = ({ graph, onUpdateAgents, agentPage }) => {
  return (
    <LeftMenuPopover>
      <LeftSidebarPopupIcon>
        <MenuItem title="Secrets">
          <FontAwesomeIcon icon={faUsers} />
        </MenuItem>
      </LeftSidebarPopupIcon>
      <LeftSidebarPopupHeader>Assistants</LeftSidebarPopupHeader>
      <LeftSidebarPopupContent>
        <SideBarAgentList
          graph={graph}
          onUpdateAgents={onUpdateAgents}
          agentPage={agentPage}
        />
      </LeftSidebarPopupContent>
    </LeftMenuPopover>
  );
};
