import psycopg
from psycopg import sql
from psycopg.sql import SQL, Composed
from typing import Any

class Database:
    def __init__(self, **kwargs):
        self.conn = psycopg.connect(**kwargs)

    def _normalize_query(self, query: str | SQL | Composed) -> SQL | Composed:
        if isinstance(query, (SQL, Composed)):
            return query
        # fallback: treat raw string as literal SQL fragment
        return Composed([sql.SQL(query)]) # type: ignore[arg-type]

    def execute(self, query: str | SQL | Composed, params: dict[str, Any] | None = None):
        q = self._normalize_query(query)
        with self.conn.cursor() as cur:
            cur.execute(q, params)
        self.conn.commit()

    def fetch_val(self, query: str | SQL | Composed, params: dict[str, Any] | None = None):
        q = self._normalize_query(query)
        with self.conn.cursor() as cur:
            cur.execute(q, params)
            row = cur.fetchone()
        self.conn.commit()
        return row[0] if row else None

    def fetch_one(self, query: str | SQL | Composed, params: dict[str, Any] | None = None):
        q = self._normalize_query(query)
        with self.conn.cursor() as cur:
            cur.execute(q, params)
            row = cur.fetchone()
        self.conn.commit()
        return row
    