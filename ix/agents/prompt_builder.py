import logging
from typing import List, Dict, Iterable

from ix.utils.count_tokens import num_tokens_from_messages

logger = logging.getLogger(__name__)


class ExceedsMaxToken(Exception):
    pass


class PromptBuilder:
    """
    A class to build text prompts with token count restrictions.

    This class allows you to create a prompt builder object with an optional tokenizer and
    a maximum token limit. By default, it uses OpenAI's tiktoken tokenizer. You can add
    clauses using the `add` method, which will raise an ExceedsMaxToken exception if the
    new string causes the total tokens to exceed the limit. The `to_prompt` method returns
    a string containing the joined clauses, separated by two newline characters.

    Example usage:

        prompt_builder = PromptBuilder(max_token_limit=20)

        try:
            prompt_builder.add("This is a sample clause.")
            prompt_builder.add("Here is another clause.")
            prompt = prompt_builder.to_prompt()
            print(prompt)
        except ExceedsMaxToken as e:
            print(e)
    """

    def __init__(
        self,
        max_token_limit: int,
        model: str = "gpt-3.5-turbo-0301",
    ):
        """
        Initialize the PromptBuilder with an optional tokenizer and max_token_limit.

        :param tokenizer: An instance of OpenAITokenizer or a custom tokenizer.
        :param max_token_limit: The maximum number of tokens allowed in the prompt.
        """
        self.model = model
        self.max_token_limit = max_token_limit
        self.messages: List[str] = []
        self.total_tokens = 0

    def count_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Count the tokens in the given text using the tokenizer.

        :param messages: The text to count tokens for.
        :return: The number of tokens in the text.
        """
        try:
            return num_tokens_from_messages(messages, self.model)
        except:
            logger.error(f"Error counting tokens for messages={messages}")
            raise

    def add(self, message: Dict[str, str]) -> int:
        """
        Add a string to the internal list of clauses.

        :param message: The text to be added as a new clause.
        :raises ExceedsMaxToken: If the new string causes the total tokens to exceed the max_token_limit.
        :return: The number of tokens in the text.
        """
        token_count = self.count_tokens([message])
        self._add(message, token_count)
        return token_count

    def _add(self, message: Dict[str, str], token_count: int):
        """Internal method for adding tokens while respecting instance token limit"""
        if (
            self.max_token_limit is not None
            and self.total_tokens + token_count > self.max_token_limit
        ):
            raise ExceedsMaxToken(
                f"Adding this string will exceed the max token limit of {self.max_token_limit}"
            )

        self.messages.append(message)
        self.total_tokens += token_count
        return token_count

    def add_max(
        self, messages: Iterable[Dict[str, str]], max_tokens: int = None
    ) -> int:
        """
        Add messages up to the local max `max_tokens`. Will also raise ExceedsMaxToken
        if instance token limit is exceeded. This method is useful for limiting categories
        of messages within the prompt. (e.g. limit chat history to `n`)

        :param messages: iterable of messages to add
        :param max_tokens: will not add more than this limit
        :return: The number of tokens added
        """
        tokens = 0
        for message in messages:
            try:
                token_count = self.count_tokens([message])
                if max_tokens and tokens + token_count > max_tokens:
                    # exceeded local max tokens
                    return tokens

                self._add(message, token_count)
                tokens += token_count

            except ExceedsMaxToken:
                # exceeded prompt max tokens
                break
        return tokens
