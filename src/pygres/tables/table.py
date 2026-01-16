from psycopg import sql
from pygres.db.database import Database
from pygres.models.base_model import PydanticTypeModel
from pygres.schema.ddl import create_table_ddl, io_relationship_ddl
from typing import Generic, Type
from pygres.types import ModelT

class PydanticTypeTable(Generic[ModelT]):
    def __init__(self, db: Database, model_cls: Type[ModelT]):
        self.db = db
        self.model_cls = model_cls

        table_name = model_cls.__name__.lower()
        self.table_name_ident = sql.Identifier(table_name)

        ddl = create_table_ddl(table_name, model_cls)
        self.db.execute(ddl)

        rel = io_relationship_ddl(table_name, model_cls)
        if rel:
            self.db.execute(rel)

    def add(self, instance: ModelT) -> ModelT:
        row = instance.to_db_row()

        col_idents = [sql.Identifier(k) for k in row.keys()]
        placeholders = [sql.Placeholder(k) for k in row.keys()]

        insert_sql = sql.SQL(
            "INSERT INTO {} ({}) VALUES ({}) RETURNING id"
        ).format(
            self.table_name_ident,
            sql.SQL(", ").join(col_idents),
            sql.SQL(", ").join(placeholders),
        )

        new_id = self.db.fetch_val(insert_sql, row)
        instance.id = new_id
        return instance
