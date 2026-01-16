import datetime
import enum
from typing import Any, get_origin, get_args

PY_TO_PG_TYPE_MAP = {
    int: "INTEGER",
    float: "DOUBLE PRECISION",
    str: "TEXT",
    bool: "BOOLEAN",
    datetime.datetime: "TIMESTAMPTZ",
    datetime.date: "DATE",
    dict: "JSONB",
    list: "JSONB",
}

def is_enum_type(t: type) -> bool:
    return isinstance(t, type) and issubclass(t, enum.Enum)

def resolve_optional(t: Any):
    origin = get_origin(t)
    if origin is None:
        return t, False

    args = get_args(t)
    non_none = [a for a in args if a is not type(None)]
    if len(non_none) == 1:
        return non_none[0], True

    return t, False

def pg_type_for(python_type: Any) -> str:
    base_type, _ = resolve_optional(python_type)

    if is_enum_type(base_type):
        return "TEXT"

    if hasattr(base_type, "model_fields"):
        return "JSONB"

    origin = get_origin(base_type)
    if origin in (list, dict):
        return "JSONB"

    # return PY_TO_PG_TYPE_MAP.get(base_type, "JSONB")
    if base_type in PY_TO_PG_TYPE_MAP:
        return PY_TO_PG_TYPE_MAP[base_type]

    # Fallback: JSONB for unknown structured types
    return "JSONB"