from copy import deepcopy

from langchain.document_loaders import WebBaseLoader

from ix.utils.importlib import import_class


def get_web_loader(**config) -> WebBaseLoader:
    """Initialize a WebBaseLoader or subclass

    Flattens setup for WebBaseLoader that isn't in the constructor.
    """
    config = deepcopy(config)
    loader_class_path = config.get("class_path")
    loader_class = import_class(loader_class_path)

    # Extract settings that need to be set directly on the instance
    requests_per_second = config.pop("requests_per_second", 2)
    default_parser = config.pop("default_parser", "html.parser")
    bs_get_text_kwargs = config.pop("bs_get_text_kwargs", {})
    raise_for_status = config.pop("raise_for_status", False)

    # initialize instance
    print(f"init with: {config}")
    loader: WebBaseLoader = loader_class(**config)
    loader.default_parser = default_parser
    loader.bs_get_text_kwargs = bs_get_text_kwargs
    loader.raise_for_status = raise_for_status
    loader.requests_per_second = requests_per_second

    return loader
