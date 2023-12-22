import inspect
from typing import Any, Type, Callable, get_type_hints, List

import pydantic
from pydantic import BaseModel, create_model

PYDANTIC_VERSION = pydantic.__version__.split(".")
PYDANTIC_MAJOR_VERSION = int(PYDANTIC_VERSION[0])


def get_model_fields(model: BaseModel):
    """v1/v2 compat for fields"""
    if PYDANTIC_MAJOR_VERSION == 2:
        return model.model_fields
    elif PYDANTIC_MAJOR_VERSION == 1:
        return model.__fields__


def from_orm(model: BaseModel, instance: Any):
    """v1/v2 compat for from_orm"""
    if PYDANTIC_MAJOR_VERSION == 2:
        return model.from_orm(instance)
    elif PYDANTIC_MAJOR_VERSION == 1:
        return model.model_validate(instance)


def create_args_model(variables, name="DynamicModel") -> Type[BaseModel]:
    """
    Dynamically create a Pydantic model class with fields for each variable
    """
    field_definitions = {field: (str, ...) for field in variables}
    return create_model(name, **field_definitions)


def fields_from_signature(func: Callable) -> dict[str, tuple[type, Any]]:
    # Extract the signature of the __init__ method
    init_signature = inspect.signature(func)

    # Get type hints, including resolving forward references
    type_hints = get_type_hints(func)

    # Prepare fields for the Pydantic model
    fields = {
        param_name: (
            type_hints.get(param_name, param.annotation),
            param.default if param.default is not inspect.Parameter.empty else ...,
        )
        for param_name, param in init_signature.parameters.items()
        if param.kind not in {param.VAR_POSITIONAL, param.VAR_KEYWORD}
        and param_name not in {"self", "cls"}
    }

    return fields


def model_from_signature(name: str, func: Callable | List[Callable]) -> Type[BaseModel]:
    """Generate a Pydantic model based on the __init__ method of a given class."""
    if isinstance(func, list):
        fields = {}
        for f in func:
            fields.update(fields_from_signature(f))
    else:
        fields = fields_from_signature(func)

    # Create the Pydantic model dynamically with arbitrary types allowed
    model_config = {"arbitrary_types_allowed": True}
    dynamic_model = create_model(name, __config__=model_config, **fields)
    return dynamic_model
