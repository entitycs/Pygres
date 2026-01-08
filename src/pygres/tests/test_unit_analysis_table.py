from psycopg.types.json import Jsonb

from pygres.examples.eg import AnalysisRow, AnalysisTable
from pygres.examples.models import AnalysisRequest, VirtualFile
from pygres.tests.base.fakedb import FakeDB

# from .models import AnalysisRow, AnalysisRequest, VirtualFile
# from table import AnalysisTable

def test_analysis_insert_basic():
    db = FakeDB()
    table = AnalysisTable(db)

    req = AnalysisRequest(
        files=[VirtualFile(path="", content="class Foo {}", language="cs")],
        knowledge=[],
        shell=[],
        options=None,
    )

    row = AnalysisRow(input=req)
    saved = table.add(row)

    # The returned row should have an ID
    assert saved.id == 42

    # The DB should have received JSONB for the input
    assert isinstance(db.last_params["input"], Jsonb) # type: ignore

    # The JSONB payload should contain the serialized request
    assert db.last_params["input"].obj["files"][0]["content"] == "class Foo {}" # type: ignore

    # The SQL should be an INSERT INTO ... RETURNING id
    sql_text = db.last_sql.as_string(None) # type: ignore
    assert "INSERT INTO" in sql_text
    assert "RETURNING id" in sql_text
