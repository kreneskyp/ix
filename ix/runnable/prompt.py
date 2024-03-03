from typing import List, Any, Dict, Optional

from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import RunnableConfig


class MultiModalChatPrompt(ChatPromptTemplate):
    """
    Extension of ChatPromptTemplate that to support images in the prompt.
    """

    def format_messages(
        self, images: List[str] = None, **kwargs: Any
    ) -> List[BaseMessage]:
        messages = super().format_messages(**kwargs)

        if images:
            images = images if isinstance(images, list) else [images]
            messages = messages + [
                HumanMessage(
                    content=[
                        {
                            "type": "image_url",
                            "image_url": {"url": image},
                        }
                    ]
                )
                for image in images
            ]

        return messages

    def _format_prompt_with_error_handling(self, inner_input: Dict):
        # auto-inject images so it's available in format_messages
        if "images" not in self.input_variables:
            self.input_variables.append("images")
        if "images" not in inner_input:
            inner_input["images"] = []
        return super()._format_prompt_with_error_handling(inner_input)


class ChatPrompt(ChatPromptTemplate):
    """Extension of ChatPromptTemplate that supports partials loaded from config."""

    def invoke(
        self, input: Dict, config: Optional[RunnableConfig] = None
    ) -> PromptValue:
        partials = (config or {}).get("partials", None)
        if partials:
            with_partials = self.partial(**partials)
            return super(ChatPrompt, with_partials).invoke(input=input, config=config)
        return super().invoke(input=input, config=config)
