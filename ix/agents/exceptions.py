from ix.task_log.models import TaskLogMessage


class AuthRequired(Exception):
    """Exception raised to break out of a chain and send an auth request to a user"""

    def __init__(self, message: TaskLogMessage):
        self.message = message


class ResponseParseError(Exception):
    """Exception thrown when response parsing fails"""


class MissingCommandMarkers(ResponseParseError):
    """Exception thrown when command markers are missing from response"""


class AgentQuestion(Exception):
    """Exception thrown when the agent needs to ask a question"""

    def __init__(self, message: str):
        self.message = message
