from typing import get_origin, get_args
from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass

def issubclass_safe(a, b):
    try:
        return issubclass(a, b)
    except Exception:
        return False


def extract_pydantic_type(annotation):
    """
    Returns the underlying Pydantic model class if the annotation
    contains one (directly or inside a container/union).
    Otherwise returns None.
    """

    # Case 1: direct model class
    if issubclass_safe(annotation, BaseModel):
        return annotation

    origin = get_origin(annotation)
    args = get_args(annotation)

    # Case 2: Optional[T] or T | None
    if origin is None and args:
        # e.g. Union[T, None]
        for arg in args:
            if issubclass_safe(arg, BaseModel):
                return arg

    # Case 3: list[T], dict[str, T], set[T], tuple[T]
    if origin in (list, dict, set, tuple):
        for arg in args:
            if issubclass_safe(arg, BaseModel):
                return arg

    return None


class PydanticTypeModelMeta(ModelMetaclass):
    # _model_registry: ClassVar[Dict[str, Any]]
    # pydantic_fields: Dict[str, Any]
    def __new__(mcls, name, bases, namespace):
        # Skip base class
        if name == "PydanticTypeModel":
            return super().__new__(mcls, name, bases, namespace)

        annotations = namespace.get("__annotations__", {})
        sql_fields = {}
        pydantic_fields = {}

        for field_name, annotation in annotations.items():
            model_type = extract_pydantic_type(annotation)

            if model_type is not None:
                pydantic_fields[field_name] = model_type
            else:
                sql_fields[field_name] = annotation

        metadata = {
            k: namespace[k]
            for k in ("create_uid", "create_io_rel")
            if k in namespace
        }

        namespace["_model_registry"] = {
            "name": name,
            "sql_fields": sql_fields,
            "pydantic_fields": pydantic_fields,
            "metadata": metadata,
        }

        return super().__new__(mcls, name, bases, namespace)