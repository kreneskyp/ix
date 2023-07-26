from typing import Any, Dict

from langchain.chat_models import ChatOpenAI


class MockChatOpenAI(ChatOpenAI):
    """Mock ChatOpenAI for testing"""

    return_value: Any = None
    raise_exception: Any = None
    acompletion_with_retry: Any = None

    def validate_environment(cls, values: Dict) -> Dict:
        return {}

    def set_return_value(self, return_value: Any):
        self.return_value = return_value

    def get_mock_content(self):
        response = self.return_value or "This is a test."
        message = {"role": "assistant", "content": None}
        if isinstance(response, dict):
            message["function_call"] = response
        else:
            message["content"] = response

        return {
            "choices": [{"message": message}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 7, "total_tokens": 12},
        }

    def completion_with_retry(self, *args, **kwargs) -> Dict[str, Any]:
        if self.raise_exception:
            raise self.raise_exception
        return self.get_mock_content()
