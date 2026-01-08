# Pygres 

### A lightweight, Pydantic‑first storage layer for persisting typed tool inputs and outputs in PostgreSQL using JSONB. 

#### Designed for development workflows, reproducible analysis, and schema‑driven introspection without the overhead of a full ORM.

## Installation

### Clone and navigate to the root repository directory

### Install requirements
```bash
uv venv .venv
source ./.venv/bin/activate
uv pip install -r requirements.txt
# for basic testing
uv pip install pytest
```

## 📘 Defining Typed Database Tables with `PydanticTypeModel` and `PydanticTypeTable`

This system provides a lightweight, explicit, and fully typed way to define PostgreSQL tables using Pydantic models.  
It automatically generates:

- PostgreSQL DDL  
- JSONB serialization/deserialization  
- Insert helpers  
- Optional self‑referential IO relationships  

All without requiring a full ORM.

---

## 🧩 Overview

A table in this system is defined using **two classes**:

1. **A row model** — inherits from `PydanticTypeModel`  
   - Describes the schema of a single row  
   - Declares which fields are nested Pydantic models (stored as JSONB)  
   - Declares which fields are SQL scalars  
   - Can opt into metadata such as `create_uid` or `create_io_rel`

2. **A table wrapper** — inherits from `PydanticTypeTable`  
   - Creates the table automatically on initialization  
   - Generates DDL from the row model  
   - Provides `.add()` for inserting rows  
   - Provides `.get()` and other helpers (if implemented)

This separation keeps schema definition clean and execution logic predictable.

---

## 🏗️ Example: Defining Tables

Below are two complete examples showing how to define a typed table.

```python
class CancellationsRow(PydanticTypeModel):
    """
    Schema for a single row in the `cancellations` table.
    Nested Pydantic models are stored as JSONB.
    Scalar fields become normal SQL columns.
    """
    output: CancellationResponse | None = None
    external_delivery_id: int | None = None
    # Optional metadata flags used by the DDL generator
    create_uid = True
    create_io_rel = True

class CancellationsTable(PydanticTypeTable):
    """
    Table wrapper for the `analysis` table; automatically 
    - generates DDL
    - binds the row model to a database connection
    - handles all SQL execution.
    """
    def __init__(self, db):
        super().__init__(db, CancellationsRow)

# another example model
class ToolAnalysisRow(PydanticTypeModel):
    input: AnalysisRequest
    output: BulkDiagramResponse | None = None
    
# completed with table and db refs
class AnalysisTable(PydanticTypeTable):
    def __init__(self, db):
        super().__init__(db, ToolAnalysisRow)
```

## Round-trip Test
#### Note: Provide your own Pydantic model(s) in place of AnalysisRequest and/or VirtualFile
#### Launch a quick postgres instance
```bash
docker run --name postgres -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_DB=testdb -p 5432:5432 -d postgres
```
#### Test Integration w/ Postgres
```python
from db.database import Database
from examples.eg import AnalysisRow, AnalysisTable
from examples.models import AnalysisRequest, VirtualFile

def test_analysis_round_trip_postgres():
    # Connect to your test DB
# With separate parameters
    db = Database(
    # conn = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="testdb",
        user="postgres",
        password="mysecretpassword"
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

    assert isinstance(reconstructed.input, AnalysisRequest)

    assert reconstructed.input.files is not None

    assert reconstructed.input.files[0].content == "class Foo {}"
```
---

## 🧠 How It Works

### ✔ Automatic DDL Generation  
When `AnalysisTable(db)` is instantiated, the system:

- inspects `AnalysisRow` via its metaclass  
- identifies Pydantic vs SQL fields  
- generates a `CREATE TABLE IF NOT EXISTS ...` statement  
- (experimental) generates a self‑referential foreign key if `create_io_rel = True`

### ✔ Automatic JSONB Handling  
Nested Pydantic models (e.g., `AnalysisRequest`, `BulkDiagramResponse`) are:

- serialized to JSONB on insert  
- deserialized back into Pydantic objects on fetch

No manual JSON handling required.

### ✔ Typed Inserts  
To insert a new row:

```python
analysis = AnalysisRow(input=req)
saved = analysis_table.add(analysis)
print(saved.id)
```

The `.add()` method:

- converts the row to a dict of SQL‑bindable values  
- builds a safe parameterized INSERT statement  
- returns the row with its assigned `id`

---

## 🚀 From Here, Where? 

This architecture gives you:

- **Pydantic validation** for all structured fields  
- **Automatic JSONB storage** for nested models  
- **Explicit, predictable SQL** without ORM magic  
- **Automatic table creation** based on your model  
- **Strong typing** across your entire data pipeline  

It’s ideal for in-development analsysis of tools, pipelines, and systems where:

- schema transparency matters
- reproducibility matters
- nested structured data is common
- you want ORM‑like convenience without ORM complexity

---

