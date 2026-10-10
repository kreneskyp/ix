import PropTypes from "prop-types";

const GoalPropTypes = {
  description: PropTypes.string.isRequired,
  complete: PropTypes.bool.isRequired,
};

const UserPropTypes = {
  id: PropTypes.string.isRequired,
  password: PropTypes.string.isRequired,
  lastLogin: PropTypes.string,
  isSuperuser: PropTypes.bool.isRequired,
  username: PropTypes.string.isRequired,
  firstName: PropTypes.string.isRequired,
  lastName: PropTypes.string.isRequired,
  email: PropTypes.string.isRequired,
  isStaff: PropTypes.bool.isRequired,
  isActive: PropTypes.bool.isRequired,
  dateJoined: PropTypes.string.isRequired,
  taskSet: PropTypes.arrayOf(PropTypes.shape(TaskPropTypes)),
};

const AgentPropTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  purpose: PropTypes.string.isRequired,
  taskSet: PropTypes.arrayOf(PropTypes.shape(TaskPropTypes)),
  tasklogmessageSet: PropTypes.arrayOf(
    PropTypes.shape(TaskLogMessagePropTypes)
  ),
};

const TaskPropTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  user: PropTypes.shape(UserPropTypes).isRequired,
  goals: PropTypes.arrayOf(PropTypes.shape(GoalPropTypes)),
  agent: PropTypes.shape(AgentPropTypes).isRequired,
  isComplete: PropTypes.bool.isRequired,
  createdAt: PropTypes.string.isRequired,
  completeAt: PropTypes.string,
  tasklogmessageSet: PropTypes.arrayOf(
    PropTypes.shape(TaskLogMessagePropTypes)
  ),
};

const TaskLogMessageRoleChoicesPropTypes = {
  SYSTEM: PropTypes.string,
  ASSISTANT: PropTypes.string,
  USER: PropTypes.string,
};

const TaskLogMessagePropTypes = {
  id: PropTypes.string.isRequired,
  task: PropTypes.shape(TaskPropTypes).isRequired,
  agent: PropTypes.shape(AgentPropTypes),
  createdAt: PropTypes.string.isRequired,
  role: PropTypes.oneOf(Object.values(TaskLogMessageRoleChoicesPropTypes))
    .isRequired,
  content: PropTypes.string.isRequired,
};
