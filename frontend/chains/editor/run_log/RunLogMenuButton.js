import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBook,
} from "@fortawesome/free-solid-svg-icons";

import { RunLogModal } from "chains/editor/run_log/RunLogModal";
import { useRunLog } from "chains/editor/run_log/useRunLog";
import { useEditorColorMode } from "chains/editor/useColorMode";
import { IndicatorIcon } from "icons/IndicatorIcon";
import { StackableIcon } from "icons/StackableIcon";
import { MenuItem } from "site/MenuItem";
import { StatusIcon } from "chains/editor/run_log/icons";

export const MenuExecutionIcon = ({ state }) => {
  const { isLight, indicator } = useEditorColorMode();
  const bg = isLight ? "gray.100" : "gray.800";
  const showIndicator =
    !state.inProgress &&
    (state.has_errors || state.has_unknown || state.completed);

  return (
    <StackableIcon>
      <FontAwesomeIcon icon={faBook} />
      {showIndicator && (
        <IndicatorIcon
          bg={bg}
          color={state.completed ? indicator.success : indicator.error}
          indicatorSize={11} // Adjust the size as needed
        >
          <StatusIcon inProgress={state.inProgress} success={state.completed} />
        </IndicatorIcon>
      )}
    </StackableIcon>
  );
};

export const RunLogMenuButton = ({}) => {
  const { state } = useRunLog();

  return (
    <RunLogModal>
      <MenuItem title={"Run Log"}>
        <MenuExecutionIcon state={state} />
      </MenuItem>
    </RunLogModal>
  );
};
