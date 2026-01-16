from psycopg import sql
from pygres.schema.introspection import columns_from_model
from typing_extensions import LiteralString
from typing import Type, cast
from pygres.types import ModelT

def create_table_ddl(table_name: str, model_cls: Type[ModelT]) -> sql.Composed:
    cols = columns_from_model(model_cls)

    column_defs: list[sql.Composed] = []
    pk_cols: list[str] = []

    for col in cols:
        col_ident = sql.Identifier(col["name"])

        pg_type = col["pg_type"]
        # pg_type is from our own mapping, not user input
        pg_type_lit = cast(LiteralString, pg_type)
        col_type = sql.SQL(pg_type_lit)

        col_def = sql.SQL("{} {}").format(col_ident, col_type)

        if not col["nullable"]:
            col_def += sql.SQL(" NOT NULL")
        
        if col["name"] == "created_at":
            col_def += sql.SQL(" DEFAULT now()")


        column_defs.append(col_def)

        if col["is_pk"]:
            pk_cols.append(col["name"])

    if pk_cols:
        pk_idents = [sql.Identifier(name) for name in pk_cols]
        pk_clause = sql.SQL("PRIMARY KEY ({})").format(sql.SQL(", ").join(pk_idents))
        column_defs.append(pk_clause)

    table_ident = sql.Identifier(table_name)

    ddl = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
        table_ident,
        sql.SQL(", ").join(column_defs),
    )

    return ddl

def io_relationship_ddl(table_name: str | sql.Identifier, model_cls: Type[ModelT]) -> sql.Composed | None:
    """
    Generate DDL for a self-referential foreign key on `input_id` → `id`
    (used for "input/output" tree-like relationships, e.g., in pipelines or IO chains).
    
    Only generated if the model explicitly opts in via metadata.
    """
    schema_info = model_cls.schema_info()
    metadata = schema_info.get("metadata", {})
    
    if not metadata.get("create_io_rel"):
        return None

    # Ensure table_name is an Identifier
    table_ident = sql.Identifier(table_name) if isinstance(table_name, str) else table_name

    # Constraint name: e.g. "mytable_input_fk"
    constraint_name = sql.Identifier(f"{table_name}_input_fk" if isinstance(table_name, str) else f"{table_name.as_string}_input_fk")

    # Build: ALTER TABLE "mytable" ADD CONSTRAINT "mytable_input_fk" FOREIGN KEY (input_id) REFERENCES "mytable" (id)
    ddl = sql.SQL("ALTER TABLE {} ADD CONSTRAINT {} FOREIGN KEY ({}) REFERENCES {} ({})").format(
        table_ident,
        constraint_name,
        sql.Identifier("input_id"),
        table_ident,           # references the same table
        sql.Identifier("id"),
    )

    return ddl