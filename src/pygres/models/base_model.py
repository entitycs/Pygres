from typing import ClassVar, Dict, Any
from pydantic import BaseModel
from psycopg.types.json import Jsonb
from pygres.models.metaclass import PydanticTypeModelMeta



class PydanticTypeModel(BaseModel, metaclass=PydanticTypeModelMeta):
    _model_registry: ClassVar[Dict[str, Any]] = {}

    id: int | None = None

    @classmethod
    def schema_info(cls):
        return cls._model_registry

    def to_db_row(self):
        row = {}
        reg = self.schema_info()

        # Serialize nested Pydantic models → JSONB
        for name in reg["pydantic_fields"]:
            value = getattr(self, name)
            if value is not None:
                row[name] = Jsonb(value.model_dump())
            else:
                row[name] = None

        # Copy scalar SQL fields
        for name in reg["sql_fields"]:
            row[name] = getattr(self, name)

        return row

    @classmethod
    def from_db_row(cls, row):
        reg = cls.schema_info()
        kwargs = {}

        # Deserialize JSONB → Pydantic
        for name, model_type in reg["pydantic_fields"].items():
            if row.get(name) is not None:
                kwargs[name] = model_type(**row[name])

        # Copy scalar SQL fields
        for name in reg["sql_fields"]:
            kwargs[name] = row.get(name)

        kwargs["id"] = row.get("id")
        return cls(**kwargs)