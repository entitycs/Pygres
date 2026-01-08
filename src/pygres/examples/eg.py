from pydantic import PrivateAttr
from pygres.examples.models import AnalysisRequest, BulkDiagramResponse
from pygres.models.base_model import PydanticTypeModel
from pygres.tables.table import PydanticTypeTable

class AnalysisRow(PydanticTypeModel):
    input: AnalysisRequest
    output: BulkDiagramResponse | None = None
    input_id: int | None = None

    _create_uid : bool = PrivateAttr(default=True)
    _create_io_rel : bool =  PrivateAttr(default=True)


class AnalysisTable(PydanticTypeTable):
    def __init__(self, db):
        super().__init__(db, AnalysisRow)
