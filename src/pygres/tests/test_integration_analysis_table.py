from pygres.db.database import Database
from pygres.examples.eg import AnalysisRow, AnalysisTable
from pygres.examples.models import AnalysisRequest, VirtualFile
from pygres.tests.config.internal_config import config
def test_analysis_round_trip_postgres():
    # Connect to your test DB
    # With separate parameters
    db = Database(
    # conn = psycopg.connect( # for reference
        host="localhost",
        port=5432,
        dbname="testdb",
        user="postgres",
        password=config.DB_PW #"mysecretpassword"
    )
    db.execute("DROP TABLE IF EXISTS analysisrow CASCADE")
    aconn = db.conn.cursor()

    table = AnalysisTable(db)

    req = AnalysisRequest(
        files=[VirtualFile(path="", content="class Foo {}", language="cs")],
        knowledge=[],
        shell=[],
        options=None,
    )

    row = AnalysisRow(input=req)
    saved = table.add(row)

    assert saved.id is not None

    # Fetch the row back manually
    aconn.execute("SELECT input, output, input_id, id FROM analysisrow WHERE id = %s", (saved.id,))
    result = aconn.fetchone()

    assert result is not None

    # Reconstruct using your from_db_row()
    reconstructed = AnalysisRow.from_db_row({
        "input": result[0],
        "output": result[1],
        "input_id": result[2],
        "id": result[3],
    })

    # Model reconstructed
    assert isinstance(reconstructed.input, AnalysisRequest)

    # Model reconstructed -> field
    assert reconstructed.input.files is not None

    # Nested model value from Pydantic Model -> field -> Pydantic Model -> Field
    assert reconstructed.input.files[0].content == "class Foo {}"