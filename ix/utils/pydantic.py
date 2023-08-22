from typing import Any

import pydantic
from pydantic import BaseModel

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
