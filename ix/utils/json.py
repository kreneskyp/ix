from dataclasses import asdict, is_dataclass
from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1


def to_json_serializable(obj: dict | BaseModel | BaseModelV1) -> dict:
    """Serialize object to json to log.

    Prefer vanilla pydantic serialization for now because LC serialization
    won't convert all objects. It is preferable to use LC serialization
    eventually to filter secrets.
    """
    if isinstance(obj, BaseModelV1):
        obj = obj.dict()
    elif isinstance(obj, BaseModel):
        obj = obj.model_dump()
    elif is_dataclass(obj):
        obj = asdict(obj)
    elif isinstance(obj, (dict, list, str, int, float, bool, type(None))):
        pass
    else:
        obj = str(obj)

    # now recursively check to make sure there are no nested objects
    # that aren't json serializable
    if isinstance(obj, dict):
        new_obj = {key: to_json_serializable(value) for key, value in obj.items()}
        obj = new_obj
    elif isinstance(obj, list):
        obj = [to_json_serializable(value) for value in obj]

    return obj
