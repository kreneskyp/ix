from typing import Dict, Any, Optional, List, Literal
from openai import OpenAI

from langchain.schema.runnable import RunnableSerializable, RunnableConfig
from langchain.schema.runnable.utils import Input
from openai.types import ImagesResponse
from pydantic.v1 import SecretStr


NO_EXTRA_DETAIL = """I NEED to test how the tool works with extremely simple prompts.
    DO NOT add any detail, just use it AS-IS:"""


DalleSizes = Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]
DefaultDefaultSize = "1024x1024"


class DalleImage(RunnableSerializable[Input, List[str]]):
    """
    Generate an image with Dalle API
    """

    input_key: str = "prompt"
    openai_api_key: Optional[SecretStr] = None
    model: str = "dall-e-3"
    n: int = 1
    """Number of images to generate"""
    size: Optional[DalleSizes] = DefaultDefaultSize
    """Size of image to generate"""
    quality: Literal["standard", "hd"] = "standard"
    separator: str = "\n"
    """Separator to use when multiple URLs are returned."""

    disable_detail_rewrite: bool = False
    """Instructs the API not to include extra detail when it rewrites the prompt."""

    @property
    def lc_secrets(self) -> Dict[str, str]:
        return {"openai_api_key": "OPENAI_API_KEY"}

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> ImagesResponse:
        client = OpenAI(api_key=self.openai_api_key)
        prompt = input[self.input_key]

        if self.disable_detail_rewrite:
            prompt = f"{NO_EXTRA_DETAIL}\n\n{prompt}"

        response = client.images.generate(
            model=self.model,
            prompt=prompt,
            size=self.size,
            quality=self.quality,
            n=self.n,
        )

        return response
