from typing import Type, TypedDict
from pygres.models.base_model import PydanticTypeModel
from pygres.schema.type_mapping import pg_type_for, resolve_optional
from pygres.types import ModelT

class ColumnSpec(TypedDict):
    name: str
    pg_type: str
    nullable: bool
    is_pk: bool

def columns_from_model(model_cls: Type[ModelT]) -> list[ColumnSpec]:
    reg = model_cls.schema_info()
    cols: list[ColumnSpec] = []

    cols.append({
        "name": "id",
        "pg_type": "SERIAL",
        "nullable": False,
        "is_pk": True,
    })

    for name in reg["pydantic_fields"]:
        cols.append({
            "name": name,
            "pg_type": "JSONB",
            "nullable": True,
            "is_pk": False,
        })

    for name, py_type in reg["sql_fields"].items():
        base_type, is_optional = resolve_optional(py_type)
        cols.append({
            "name": name,
            "pg_type": pg_type_for(base_type),
            "nullable": is_optional,
            "is_pk": False,
        })

    if reg["metadata"].get("create_uid"):
        cols.append({
            "name": "created_at",
            "pg_type": "TIMESTAMPTZ",
            "nullable": False,
            "is_pk": False,
        })

    return cols
