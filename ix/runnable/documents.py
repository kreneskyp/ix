from typing import (
    Sequence,
    Optional,
    Any,
    Dict,
    Type,
    AsyncIterator,
    Iterator,
    Callable,
)
from pydantic.v1 import BaseConfig

from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document, BaseDocumentTransformer
from langchain_core.runnables import RunnableSerializable, RunnableConfig
from langchain_core.runnables.utils import Input


from ix.utils.pydantic import model_from_signature
from ix.utils.importlib import import_class


class RunTransformer(RunnableSerializable[Sequence[Document], Sequence[Document]]):
    """Runnable shim to treat a DocumentTransformer as a Runnable.

    BaseDocumentTransformer are not runnables so they need a shim to fit
    into a flow.
    """

    transformer: BaseDocumentTransformer

    class Config(BaseConfig):
        arbitrary_types_allowed = True

    def invoke(
        self,
        input: Sequence[Document],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Sequence[Document]:
        return self.transformer.transform_documents(input)

    async def ainvoke(
        self,
        input: Sequence[Document],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Sequence[Document]:
        resp = await self.transformer.atransform_documents(input)
        return resp

    @classmethod
    def from_config(cls, class_path: str, config: Dict[str, Any]) -> "RunTransformer":
        """Initialize a RunTransformer from a config dict."""
        initializer = import_class(class_path)
        transformer = initializer(**config)
        return cls(transformer=transformer)


class RunLoader(RunnableSerializable[Input, Sequence[Document]]):
    """Runnable shim to treat a BaseLoader as a Runnable.

    BaseLoader are not a Runnable, so they require a shim to integrate into a flow.
    The shim generically integrates BaseLoaders by dynamically generating the input
     type from the loader's __init__ method.

    Fields may be configured in the config dict or from input. Input and configured fields
    are merged at runtime. Values from input have precedence.
    """

    initializer: Type[BaseLoader] | Callable[..., BaseLoader]
    config: Dict[str, Any]

    class Config(BaseConfig):
        arbitrary_types_allowed = True

    # TODO: does it make more sense to use the NodeType's schema here?
    @property
    def InputType(self) -> Type[Input]:
        """Dynamically generate a Pydantic model for the loader's __init__ method."""
        if hasattr(self.initializer, "__name__"):
            name = self.initializer.__name__
        else:
            name = "Input"

        return model_from_signature(name, self.initializer)

    def get_loader(self, input: Input) -> BaseLoader:
        """Get a BaseLoader instance initialized with field values
        merged from input and config."""
        # merge and validate input
        merged_config = self.config.copy()
        field_names = self.InputType.__fields__.keys()
        for field in field_names:
            if field in input:
                merged_config[field] = input[field]
        validated = self.InputType(**merged_config)

        # create instance
        return self.initializer(**validated.dict())

    def invoke(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Sequence[Document]:
        loader = self.get_loader(input)
        return loader.load()

    async def ainvoke(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Sequence[Document]:
        loader = self.get_loader(input)
        return loader.load()

    def stream(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ) -> Iterator[Document]:
        """Stream documents from the loader.

        Documents will be streamed from the loader if it supports `BaseLoader.lazy_load()`.
        Otherwise, documents will be loaded synchronously and then yielded to emulate a stream.
        """
        loader = self.get_loader(input)

        # attempt to use lazy load iterator
        if loader.lazy_load != BaseLoader.lazy_load:
            for doc in loader.lazy_load():
                yield doc
        else:
            # fall back to loading all at once
            for doc in loader.load():
                yield doc

    async def astream(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[Document]:
        """Stream documents from the loader.

        Documents will be streamed from the loader if it supports `BaseLoader.lazy_load()`.
        Otherwise, documents will be loaded synchronously and then yielded to emulate a stream.
        """
        loader = self.get_loader(input)

        # attempt to use lazy load iterator
        if loader.lazy_load != BaseLoader.lazy_load:
            for doc in loader.lazy_load():
                yield doc
        else:
            # fall back to loading all at once
            for doc in loader.load():
                yield doc

    @classmethod
    def from_config(cls, class_path: str, config: Dict[str, Any]) -> "RunLoader":
        """Initialize a RunTransformer from a config dict and class_path.

        Integration point for component loader.
        """
        initializer = import_class(class_path)
        return cls(initializer=initializer, config=config)
