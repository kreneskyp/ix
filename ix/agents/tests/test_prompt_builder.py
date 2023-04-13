import pytest
from ix.agents.prompt_builder import PromptBuilder, ExceedsMaxToken


class TestPromptBuilder:
    system_msg = {"role": "system", "content": "this is a system message"}
    assistant_msg = {"role": "assistant", "content": "this is an assistant message"}
    user_msg = {"role": "user", "content": "this is a user message"}

    def test_init(self):
        """
        Test that the PromptBuilder can be initialized with a max_token_limit and a model.
        """
        pb = PromptBuilder(max_token_limit=20, model="gpt-3.5-turbo-0301")
        assert pb.max_token_limit == 20
        assert pb.model == "gpt-3.5-turbo-0301"

    def test_count_tokens_single_message(self):
        """
        Test that the count_tokens method returns the correct token count for a single message.
        """
        pb = PromptBuilder(max_token_limit=100)
        token_count = pb.count_tokens([self.system_msg])
        assert token_count > 0

    def test_count_tokens_multiple_messages(self):
        """
        Test that the count_tokens method returns the correct token count for multiple messages.
        """
        pb = PromptBuilder(max_token_limit=100)
        token_count = pb.count_tokens(
            [self.system_msg, self.assistant_msg, self.user_msg]
        )
        assert token_count > 0

    def test_add_message(self):
        """
        Test that the add method correctly adds a message and updates the total token count.
        """
        pb = PromptBuilder(max_token_limit=100)
        initial_tokens = pb.total_tokens
        token_count = pb.add(self.system_msg)
        assert pb.total_tokens == initial_tokens + token_count

    def test_add_exceeds_max_token(self):
        """
        Test that the add method raises an ExceedsMaxToken exception when adding a message that exceeds the max_token_limit.
        """
        pb = PromptBuilder(max_token_limit=1)
        with pytest.raises(ExceedsMaxToken):
            pb.add(self.system_msg)

    def test_add_returns_token_count(self):
        """
        Test that the add method returns the correct token count for the added message.
        """
        pb = PromptBuilder(max_token_limit=100)
        token_count = pb.add(self.system_msg)
        assert token_count > 0

    def test_add_max_local(self):
        """
        Test that the add_max method adds messages up to the local max_tokens parameter.
        """
        pb = PromptBuilder(max_token_limit=100)
        pb.add_max([self.system_msg, self.assistant_msg, self.user_msg], max_tokens=5)
        assert pb.total_tokens <= 5

    def test_add_max_global(self):
        """
        Test that the add_max method stops adding messages when the max_token_limit is reached.
        """
        pb = PromptBuilder(max_token_limit=10)
        pb.add_max([self.system_msg, self.assistant_msg, self.user_msg])
        assert pb.total_tokens <= 10

    def test_add_max_no_limit(self):
        """
        Test that the add_max method works correctly with no max_tokens parameter.
        """
        pb = PromptBuilder(max_token_limit=None)
        pb.add_max([self.system_msg, self.assistant_msg, self.user_msg])
        assert pb.total_tokens > 0
