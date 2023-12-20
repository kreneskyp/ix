import importlib
import logging
from typing import Type


logger = logging.getLogger(__name__)


def _import_class(class_path: str) -> Type:
    """
    inner class to facilitate test mocking across all uses of `import_class`
    """
    try:
        module_path, class_name = class_path.rsplit(".", 1)
    except Exception as e:
        logger.error(
            f"Error splitting class_path={class_path} into module and class name: {e}"
        )
        raise e

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        if "." in module_path:
            property_name = class_name
            module_path, class_name = module_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            class_ = getattr(module, class_name)
            return getattr(class_, property_name)
        else:
            raise ModuleNotFoundError(f"Module {module_path} not found")

    return getattr(module, class_name)


def import_class(class_path: str) -> Type:
    """
    Import a class from a string representation of its fully qualified name.

    Args:
        class_path: A string that represents the fully qualified name of the class to import.

    Returns:
        The imported class object.
    """
    return _import_class(class_path)
