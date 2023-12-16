import React from "react";
import { Box, Spinner, Text, Tooltip } from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faCheckCircle,
  faCircleExclamation,
  faCircleQuestion,
  faSync,
} from "@fortawesome/free-solid-svg-icons";
import { useRunLog } from "chains/editor/run_log/useRunLog";

const SPIN_CSS = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

export const InProgressIcon = (props) => {
  return (
    <Box
      color={"green.400"}
      display="inline-block"
      animation="spin 1s infinite linear"
      css={SPIN_CSS}
      {...props}
    >
      <FontAwesomeIcon icon={faSync} />
    </Box>
  );
};

export const SuccessIcon = (props) => {
  return (
    <Text color={"green.400"} {...props}>
      <FontAwesomeIcon icon={faCheckCircle} />
    </Text>
  );
};

export const ErrorIcon = (props) => {
  return (
    <Text color={"red.400"} {...props}>
      <FontAwesomeIcon icon={faCircleExclamation} />
    </Text>
  );
};

export const UnknownIcon = (props) => {
  return (
    <Text color={"yellow.400"} {...props}>
      <FontAwesomeIcon icon={faCircleQuestion} />
    </Text>
  );
};

export const StatusIcon = ({ inProgress, success, ...props }) => {
  if (inProgress === true) {
    return <InProgressIcon {...props} />;
  } else if (success === true) {
    return <SuccessIcon {...props} />;
  } else if (success === false) {
    return <ErrorIcon {...props} />;
  } else {
    return <UnknownIcon {...props} />;
  }
};

export const ExecutionStatusIcon = ({ execution, ...props }) => {
  const inProgress = execution.finished_at === null;
  return (
    <StatusIcon
      inProgress={inProgress}
      success={execution.completed}
      {...props}
    />
  );
};

export const RunLogStatusIcon = (props) => {
  const { log } = useRunLog();
  const has_inprogress = log?.executions.some((e) => e.finished_at === null);
  const has_errors = log?.executions.some((e) => e.completed === false);
  const has_unknown = log?.executions.some((e) => e.completed === null);
  const success =
    !has_inprogress && has_errors ? false : has_unknown ? null : true;
  return (
    <StatusIcon inProgress={has_inprogress} success={success} {...props} />
  );
};
