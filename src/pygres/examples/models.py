from pydantic import BaseModel, Field
from typing import List

class VirtualFile(BaseModel):
    """
    VirtualFile can be a string of text representing a file, a path to a directory of files, or the path to a single file.
    """
    content: str | None = Field(
        None,
        description="Inline file content. Use this parameter when a string representing code is given. This should include all blocks of code string in their entirety."
    )
    path: str | None = Field(
        None,
        description="Absolute or container-relative path. Required if content is not provided. Ignored if content is provided."
    )
    language: str | None = Field(
        None,
        description="Optional language hint (cs, py, json, etc.).  These may be described implicity, or explicitly via code block markers like ```cs."
    )

    model_config = {
        "extra": "forbid"
    }

class KnowledgeBlob(BaseModel):
    kind: str | None = Field(
        None,
        description="Type of knowledge (summary, ast, symbols, diagram, schema, notes, etc.)"
    )
    payload: str = Field(
        ...,
        description="Raw knowledge content. Could be JSON, text, mermaid, etc."
    )
    metadata: dict[str, object] | None = Field(
        None,
        description="Optional metadata describing the payload."
    )

    model_config = {
        "extra": "forbid"
    }

class ShellCapture(BaseModel):
    command: str | None = Field(
        None,
        description="The command that produced this output."
    )
    stdout: str = Field(
        ...,
        description="Captured standard output."
    )
    stderr: str | None = Field(
        None,
        description="Captured standard error."
    )
    exit_code: int | None = Field(
        None,
        description="Exit code of the command."
    )

    model_config = {
        "extra": "forbid"
    }

class DiagramItemRequest(BaseModel):
    """
    Format of request to retrieve a mermaid diagram from source code given a path (file path or filename).
    """
    source_file_path: str = Field(..., description="Filename or file path from which to generate a diagram")

class BatchCreateClassDiagramRequest(BaseModel):
    """
    Format of request to retrieve one or more mermaid diagrams from source code given a path (file path or filename), or from the current workspace 
    """
    source_folder_path: str | None = Field("/workspace/src", description="Path to folder containing .cs files")
    max_files: int | None = Field(10, ge=1, le=1000)
    include_interfaces: bool | None = True # note - likely to deprecate
    include_abstracts: bool | None = True

class ToolOptions(BaseModel):
    diagram_item: DiagramItemRequest | None = None
    batch_create: BatchCreateClassDiagramRequest | None = None
    model_config = {"extra": "forbid"}

class AnalysisRequest(BaseModel):
    files: list[VirtualFile] | None = Field(
        None,
        description="List of files to analyze, from disk or inline."
    )
    knowledge: list[KnowledgeBlob] | None = Field(
        None,
        description="Arbitrary knowledge sources provided by the model."
    )
    shell: list[ShellCapture] | None = Field(
        None,
        description="Shell command outputs to incorporate into analysis."
    )
    options: ToolOptions | None = Field(
        None,
        description="Tool-specific options (mode, flags, thresholds, etc.)"
    )

    model_config = {
        "extra": "forbid"
    }

class DiagramItem(BaseModel):
    """
    Format of response to retrieve a single mermaid diagrams from a file given its file path or filename.
    """
    file: str = Field(..., description="Relative path or filename of the source file")
    diagram: str = Field(..., description="Mermaid Diagram code for type classDiagram")


class BulkDiagramResponse(BaseModel):
    """
    Format of response to retrieve one or more mermaid diagrams from source code given a path (file path or filename), or from the current workspace.
    """
    content: List[DiagramItem] = Field(..., description="List of processed mermaid diagrams")
    processed: int = Field(..., description="Number of files processed")
    truncated: bool = Field(False, description="True if stopped early due to max_files")
    total_scanned: int = Field(0, description="Total .cs files found before limit")
