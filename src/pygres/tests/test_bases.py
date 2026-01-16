from pygres.examples.eg import AnalysisRow, AnalysisTable
from pygres.examples.models import AnalysisRequest
from pygres.tests.base.fakedb import FakeDB

def test_simple_insert():
    db = FakeDB()
    table = AnalysisTable(db)

    req = AnalysisRequest(files=[], knowledge=[], shell=[], options=None)
    analysis = AnalysisRow(input=req)

    saved = table.add(analysis)

    assert saved.id == 42
    